# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
from datetime import datetime
from utils.config_manager import ConfigManager

class ApplicationForm(Modal, title='Заявка в Price FamQ'):
    """Форма заявки в семью"""
    
    name = TextInput(
        label='Ваше имя и фамилия (RP)',
        placeholder='Например: John Price',
        required=True,
        max_length=50
    )
    
    age = TextInput(
        label='Возраст персонажа',
        placeholder='Например: 25',
        required=True,
        max_length=3
    )
    
    experience = TextInput(
        label='Опыт игры на сервере',
        placeholder='Расскажите о вашем опыте игры в GTA 5 RP',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )
    
    why_family = TextInput(
        label='Почему хотите вступить в Price FamQ?',
        placeholder='Расскажите, почему выбрали именно нашу семью',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )
    
    about_yourself = TextInput(
        label='Расскажите о себе',
        placeholder='Немного о вас и вашем персонаже',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = ConfigManager()

    async def on_submit(self, interaction: discord.Interaction):
        """Обработка отправки заявки"""
        # ВАЖНО: Сначала отвечаем на interaction!
        await interaction.response.send_message(
            'Ваша заявка отправлена! Ожидайте рассмотрения.',
            ephemeral=True
        )
        
        # Создаем красивый embed с заявкой и эмодзи
        embed = discord.Embed(
            title='📝 Новая заявка в семью',
            description=f'👤 **Кандидат:** {interaction.user.mention}\n📅 **Дата:** <t:{int(datetime.now().timestamp())}:F>',
            color=self.config.get_color('primary'),
            timestamp=datetime.now()
        )
        
        
        embed.add_field(
            name='🎭 Имя персонажа', 
            value=self.name.value, 
            inline=True
        )
        embed.add_field(
            name='🎂 Возраст', 
            value=f'{self.age.value} лет', 
            inline=True
        )
        embed.add_field(
            name='💬 Discord', 
            value=f'{interaction.user.name}', 
            inline=True
        )
        
        embed.add_field(
            name='🎮 Опыт игры', 
            value=self.experience.value, 
            inline=False
        )
        embed.add_field(
            name='💎 Почему Price FamQ?', 
            value=self.why_family.value, 
            inline=False
        )
        embed.add_field(
            name='✨ О себе', 
            value=self.about_yourself.value, 
            inline=False
        )
        
        embed.set_footer(
            text=f'🆔 ID: {interaction.user.id}',
        )
        
        # Получаем канал рассмотрения СНАЧАЛА
        review_channel_id = self.config.get('review_channel_id')
        review_channel = self.bot.get_channel(review_channel_id)
        
        if not review_channel:
            await interaction.followup.send(
                '❌ Канал рассмотрения не настроен! Обратитесь к администратору.',
                ephemeral=True
            )
            return
        
        # Получаем ID ролей модераторов для упоминания
        moderator_role_ids = self.config.get('moderator_role_ids', [])
        mention_roles = []

        for role_id in moderator_role_ids:
            role = review_channel.guild.get_role(role_id)
            if role:
                mention_roles.append(role.mention)

        # Создаем текстовое сообщение с упоминанием ролей
        mention_text = " ".join(mention_roles) if mention_roles else "@here"
        message_content = f"{mention_text} 📝 Новая заявка!"
        
        # Создаем кнопки для рассмотрения
        view = ApplicationReviewView(self.bot, interaction.user.id)

        try:
            await review_channel.send(content=message_content, embed=embed, view=view)
            
            # Логирование
            await self._log_application(interaction.user, "подана")
            
            # Успешное сообщение пользователю
            await interaction.followup.send(
                '✅ Ваша заявка успешно отправлена на рассмотрение!',
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                '❌ Ошибка: нет доступа к каналу рассмотрения.',
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f'❌ Ошибка при отправке заявки: {e}',
                ephemeral=True
            )
    
    async def _log_application(self, user: discord.User, status: str):
        """Логирование заявки"""
        logs_channel_id = self.config.get('logs_channel_id')
        if not logs_channel_id:
            return
        
        logs_channel = self.bot.get_channel(logs_channel_id)
        if not logs_channel:
            return
        
        embed = discord.Embed(
            title='📝 Заявка в семью',
            description=f'{user.mention} {status} заявку',
            color=self.config.get_color('info'),
            timestamp=datetime.now()
        )
        embed.add_field(name='Пользователь', value=f'{user.name} ({user.id})', inline=False)
        
        try:
            await logs_channel.send(embed=embed)
        except:
            pass


class RejectReasonModal(Modal, title='Причина отклонения'):
    """Модальное окно для причины отклонения"""
    
    reason = TextInput(
        label='Укажите причину отклонения',
        placeholder='Напишите причину, по которой заявка отклонена',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )
    
    def __init__(self, bot, user_id: int, original_embed: discord.Embed, original_message: discord.Message):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.original_embed = original_embed
        self.original_message = original_message
        self.config = ConfigManager()
    
    async def on_submit(self, interaction: discord.Interaction):
        """Обработка отклонения заявки"""
        user = await self.bot.fetch_user(self.user_id)
        
        # Уведомляем пользователя об отклонении
        reject_embed = discord.Embed(
            title='❌ Заявка отклонена',
            description='😔 Ваша заявка в Price FamQ была отклонена.',
            color=self.config.get_color('error'),
            timestamp=datetime.now()
        )
        
        
        reject_embed.add_field(name='📋 Причина', value=self.reason.value, inline=False)
        reject_embed.add_field(
            name='💡 Что дальше?',
            value='Вы можете подать новую заявку после устранения указанных замечаний.',
            inline=False
        )
        reject_embed.set_footer(text='💎 Price FamQ')
        
        try:
            await user.send(embed=reject_embed)
        except discord.Forbidden:
            pass
        
        # Обновляем оригинальное сообщение
        self.original_embed.color = self.config.get_color('error')
        self.original_embed.add_field(
            name='❌ Статус',
            value=f'**Отклонена** модератором {interaction.user.mention}\n📋 **Причина:** {self.reason.value}',
            inline=False
        )
        
        await self.original_message.edit(embed=self.original_embed, view=None)
        
        # Логирование
        await self._log_action(interaction.user, user, "отклонил", self.reason.value)
        
        await interaction.response.send_message(
            f'✅ Заявка отклонена. Пользователь уведомлен.',
            ephemeral=True
        )
    
    async def _log_action(self, moderator: discord.User, applicant: discord.User, action: str, reason: str = None):
        """Логирование действия модератора"""
        logs_channel_id = self.config.get('logs_channel_id')
        if not logs_channel_id:
            return
        
        logs_channel = self.bot.get_channel(logs_channel_id)
        if not logs_channel:
            return
        
        embed = discord.Embed(
            title=f'🔴 Заявка отклонена',
            color=self.config.get_color('error'),
            timestamp=datetime.now()
        )
        embed.add_field(name='Модератор', value=moderator.mention, inline=True)
        embed.add_field(name='Заявитель', value=applicant.mention, inline=True)
        if reason:
            embed.add_field(name='Причина', value=reason, inline=False)
        
        try:
            await logs_channel.send(embed=embed)
        except:
            pass


class ApplicationReviewView(View):
    """Кнопки для рассмотрения заявки"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.config = ConfigManager()
    
    def _check_permissions(self, interaction: discord.Interaction) -> bool:
        """Проверка прав на рассмотрение заявок"""
        # Получаем все необходимые ID ролей из конфига
        moderator_role_ids = self.config.get('moderator_role_ids', [])  # REC, Cur.REC
        owner_role_ids = self.config.get('owner_role_ids', [])  # Owner
        dep_owner_role_ids = self.config.get('dep_owner_role_ids', [])  # Dep.Owner
        dev_role_ids = self.config.get('dev_role_ids', [])  # Developer
        
        # Собираем все разрешенные роли в один список
        allowed_role_ids = moderator_role_ids + owner_role_ids + dep_owner_role_ids + dev_role_ids
        
        # Проверяем есть ли у пользователя хоть одна разрешенная роль
        return any(role.id in allowed_role_ids for role in interaction.user.roles)
    
    @discord.ui.button(label='📋 Рассмотреть', style=discord.ButtonStyle.primary, custom_id='review')
    async def review_button(self, interaction: discord.Interaction, button: Button):
        """Взять заявку на рассмотрение"""
        if not self._check_permissions(interaction):
            await interaction.response.send_message(
                '❌ У вас нет прав для рассмотрения заявок!',
                ephemeral=True
            )
            return
        
        # Обновляем embed
        embed = interaction.message.embeds[0]
        embed.add_field(
            name='👀 На рассмотрении',
            value=f'Рассматривает: {interaction.user.mention}',
            inline=False
        )
        embed.color = self.config.get_color('warning')
        
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message(
            '✅ Вы взяли заявку на рассмотрение.',
            ephemeral=True
        )
        
        # Логирование
        await self._log_action(interaction.user, self.user_id, "взял на рассмотрение")
    
    @discord.ui.button(label='✅ Одобрить', style=discord.ButtonStyle.success, custom_id='approve')
    async def approve_button(self, interaction: discord.Interaction, button: Button):
        """Одобрить заявку"""
        if not self._check_permissions(interaction):
            await interaction.response.send_message(
                '❌ У вас нет прав для одобрения заявок!',
                ephemeral=True
            )
            return
        
        user = await self.bot.fetch_user(self.user_id)
        guild = interaction.guild
        member = guild.get_member(self.user_id)
        
        # Выдаем роль Price Academy
        member_role_id = self.config.get('member_role_id')
        if member and member_role_id:
            role = guild.get_role(member_role_id)
            if role:
                try:
                    await member.add_roles(role)
                except discord.Forbidden:
                    await interaction.response.send_message(
                        'Не удалось выдать роль. Проверьте права бота.',
                        ephemeral=True
                    )
        
        # Уведомляем пользователя
        approve_embed = discord.Embed(
            title='✅ Заявка одобрена!',
            description='🎉 **Поздравляем! Вы приняты в Price FamQ!**',
            color=self.config.get_color('success'),
            timestamp=datetime.now()
        )
        
        
        approve_embed.add_field(
            name='👋 Добро пожаловать',
            value='Вам выдана роль **Price Academy**. Начните свой путь в семье!',
            inline=False
        )
        approve_embed.set_footer(text='💎 Price FamQ')
        
        try:
            await user.send(embed=approve_embed)
        except discord.Forbidden:
            pass
        
        # Обновляем оригинальное сообщение
        embed = interaction.message.embeds[0]
        embed.color = self.config.get_color('success')
        embed.add_field(
            name='✅ Статус',
            value=f'**Одобрена** • {interaction.user.mention}',
            inline=False
        )
        
        await interaction.message.edit(embed=embed, view=None)
        
        # Логирование
        await self._log_action(interaction.user, self.user_id, "одобрил")
        
        await interaction.response.send_message(
            f'✅ Заявка одобрена! {user.mention} получил роль Price Academy.',
            ephemeral=True
        )
    
    @discord.ui.button(label='❌ Отклонить', style=discord.ButtonStyle.danger, custom_id='reject')
    async def reject_button(self, interaction: discord.Interaction, button: Button):
        """Отклонить заявку"""
        if not self._check_permissions(interaction):
            await interaction.response.send_message(
                '❌ У вас нет прав для отклонения заявок!',
                ephemeral=True
            )
            return
        
        # Открываем модальное окно для указания причины
        modal = RejectReasonModal(
            self.bot,
            self.user_id,
            interaction.message.embeds[0],
            interaction.message
        )
        await interaction.response.send_modal(modal)
    
    async def _log_action(self, moderator: discord.User, applicant_id: int, action: str):
        """Логирование действия модератора"""
        logs_channel_id = self.config.get('logs_channel_id')
        if not logs_channel_id:
            return
        
        logs_channel = self.bot.get_channel(logs_channel_id)
        if not logs_channel:
            return
        
        applicant = await self.bot.fetch_user(applicant_id)
        
        color_map = {
            "взял на рассмотрение": self.config.get_color('warning'),
            "одобрил": self.config.get_color('success')
        }
        
        embed = discord.Embed(
            title=f'{"🟢" if action == "одобрил" else "🟠"} Заявка {action}',
            color=color_map.get(action, self.config.get_color('info')),
            timestamp=datetime.now()
        )
        embed.add_field(name='Модератор', value=moderator.mention, inline=True)
        embed.add_field(name='Заявитель', value=applicant.mention, inline=True)
        
        try:
            await logs_channel.send(embed=embed)
        except:
            pass


class ApplicationButton(View):
    """Кнопка для подачи заявки"""
    
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(
        label='📝 Подать заявку в семью',
        style=discord.ButtonStyle.primary,
        custom_id='apply',
        emoji='✨'
    )
    async def apply_button(self, interaction: discord.Interaction, button: Button):
        """Обработка нажатия кнопки заявки"""
        modal = ApplicationForm(self.bot)
        await interaction.response.send_modal(modal)


class Applications(commands.Cog):
    """Модуль управления заявками"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()
        
        # Добавляем persistent views
        self.bot.add_view(ApplicationButton(bot))
        # Создаем пустой view для восстановления кнопок рассмотрения
        self.bot.add_view(ApplicationReviewView(bot, 0))
    
    @commands.command(name='setup_application')
    @commands.has_permissions(administrator=True)
    async def setup_application(self, ctx):
        """Создает сообщение с кнопкой подачи заявки"""
        embed = discord.Embed(
            title='📝 Заявка в Price FamQ',
            description='👋 Хочешь стать частью нашей семьи? Заполни заявку ниже.',
            color=self.config.get_color('primary')
        )
        
        
        embed.add_field(
            name='📋 Требования',
            value='• 🎂 Возраст 16+\n• 🎤 Микрофон обязателен\n• 🎭 Знание основ RP\n• ⚡ Активность на сервере',
            inline=False
        )
        
        embed.add_field(
            name='✅ После одобрения',
            value='Вы получите роль **Price Academy** и сможете начать свой путь в семье!',
            inline=False
        )
        
        embed.set_footer(
            text='💎 Price FamQ • Нажми на кнопку ниже',
        )
        
        
        
        view = ApplicationButton(self.bot)
        await ctx.send(embed=embed, view=view)
        
        try:
            await ctx.message.delete()
        except:
            pass


    @commands.command(name='clear_old_applications')
    @commands.has_permissions(administrator=True)
    async def clear_old_applications(self, ctx, limit: int = 50):
        """Очистить старые заявки с кнопками (Owner/Developer)"""
        review_channel_id = self.config.get('review_channel_id')
        
        if not review_channel_id:
            await ctx.send('❌ Канал рассмотрения не настроен!')
            return
        
        review_channel = self.bot.get_channel(review_channel_id)
        
        if not review_channel:
            await ctx.send('❌ Канал рассмотрения не найден!')
            return
        
        await ctx.send(f'🔄 Обрабатываю последние {limit} сообщений...')
        
        edited_count = 0
        deleted_count = 0
        
        try:
            async for message in review_channel.history(limit=limit):
                # Пропускаем сообщения без embeds
                if not message.embeds:
                    continue
                
                # Проверяем что это заявка
                embed = message.embeds[0]
                if not embed.title or 'Новая заявка' not in embed.title:
                    continue
                
                # Проверяем есть ли кнопки
                if not message.components:
                    continue
                
                try:
                    # Удаляем кнопки из старой заявки
                    await message.edit(view=None)
                    edited_count += 1
                except:
                    pass
            
            await ctx.send(f'✅ Обработано заявок: {edited_count}\n'
                          f'Удалено кнопок у {edited_count} сообщений.')
        
        except Exception as e:
            await ctx.send(f'❌ Ошибка: {e}')


async def setup(bot):
    """Функция загрузки cog"""
    await bot.add_cog(Applications(bot))