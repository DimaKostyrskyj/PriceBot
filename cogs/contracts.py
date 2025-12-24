# -*- coding: utf-8 -*-
# contracts.py - СТИЛЬ КАК В ПРИМЕРЕ, АДАПТИРОВАН ПОД PRICE FAMQ
import discord
from discord.ext import commands, tasks
from discord.ui import Modal, TextInput, View, Button
from datetime import datetime
from utils.config_manager import ConfigManager


class ContractView(View):
    """View с кнопками для контракта"""
    
    def __init__(self, message=None, participants=None):
        super().__init__(timeout=None)
        self.message = message
        self.participants = participants if participants is not None else []
        self.config = ConfigManager()
        self.started = False
    
    @discord.ui.button(
        label='Записаться',
        style=discord.ButtonStyle.success,
        emoji='🟢',
        custom_id='contract_join'
    )
    async def join_button(self, interaction: discord.Interaction, button: Button):
        """Кнопка записи на контракт"""
        user_id = interaction.user.id
        
        if user_id in self.participants:
            await interaction.response.send_message(
                '❌ Вы уже записаны на этот контракт!',
                ephemeral=True
            )
            return
        
        self.participants.append(user_id)
        
        # Обновляем embed
        await self.update_embed(interaction)
        
        await interaction.response.send_message(
            '✅ Вы записались на контракт!',
            ephemeral=True
        )
    
    @discord.ui.button(
        label='Выписаться',
        style=discord.ButtonStyle.danger,
        emoji='🔴',
        custom_id='contract_leave'
    )
    async def leave_button(self, interaction: discord.Interaction, button: Button):
        """Кнопка выписки с контракта"""
        user_id = interaction.user.id
        
        if user_id not in self.participants:
            await interaction.response.send_message(
                '❌ Вы не записаны на этот контракт!',
                ephemeral=True
            )
            return
        
        self.participants.remove(user_id)
        
        # Обновляем embed
        await self.update_embed(interaction)
        
        await interaction.response.send_message(
            '✅ Вы выписались с контракта!',
            ephemeral=True
        )
    
    @discord.ui.button(
        label='Начать контракт',
        style=discord.ButtonStyle.primary,
        emoji='▶️',
        custom_id='contract_start'
    )
    async def start_button(self, interaction: discord.Interaction, button: Button):
        """Кнопка начала контракта (только для Contract и Owner)"""
        # Проверяем права
        contract_role_id = self.config.get('contract_role_id', 0)
        owner_role_ids = self.config.get('owner_role_ids', [])
        
        user_role_ids = [role.id for role in interaction.user.roles]
        
        has_permission = False
        if contract_role_id and contract_role_id in user_role_ids:
            has_permission = True
        if any(role_id in user_role_ids for role_id in owner_role_ids):
            has_permission = True
        
        if not has_permission:
            await interaction.response.send_message(
                '❌ Вы дебил! У вас нет прав!!! Требуется роль Contract или Owner.',
                ephemeral=True
            )
            return
        
        self.started = True
        
        # Обновляем embed
        message = interaction.message
        embed = message.embeds[0]
        
        # Меняем статус
        for i, field in enumerate(embed.fields):
            if field.name == "🟢 Статус:":
                embed.set_field_at(
                    i,
                    name="🔵 Статус:",
                    value="⏳ Контракт начат!",
                    inline=False
                )
                break
        
        # Создаем новый View только с кнопкой "Закончить"
        new_view = ContractFinishView()
        
        await message.edit(embed=embed, view=new_view)
        
        # Отправляем сообщение в ветку
        if message.thread:
            await message.thread.send(
                f'✅ Контракт начат! Начал: {interaction.user.mention}'
            )
        
        await interaction.response.send_message(
            '✅ Контракт начат!',
            ephemeral=True
        )
    
    async def update_embed(self, interaction: discord.Interaction):
        """Обновление embed с участниками"""
        message = interaction.message
        embed = message.embeds[0]
        
        # Формируем список участников
        if self.participants:
            participants_list = []
            for user_id in self.participants:
                user = interaction.guild.get_member(user_id)
                if user:
                    participants_list.append(f"✅ {user.mention}")
            
            participants_text = "\n".join(participants_list) if participants_list else "❌ Пока нет участников"
        else:
            participants_text = "❌ Пока нет участников"
        
        # Обновляем поле участников
        for i, field in enumerate(embed.fields):
            if field.name == "📊 Участники:":
                embed.set_field_at(
                    i,
                    name="📊 Участники:",
                    value=participants_text,
                    inline=False
                )
                break
        
        await message.edit(embed=embed, view=self)


class ContractFinishView(View):
    """View с кнопкой завершения контракта"""
    
    def __init__(self):
        super().__init__(timeout=None)
        self.config = ConfigManager()
    
    @discord.ui.button(
        label='Закончить',
        style=discord.ButtonStyle.danger,
        emoji='⏹️',
        custom_id='contract_finish'
    )
    async def finish_button(self, interaction: discord.Interaction, button: Button):
        """Кнопка завершения контракта"""
        # Обновляем embed
        message = interaction.message
        embed = message.embeds[0]
        
        # Меняем статус на завершен
        for i, field in enumerate(embed.fields):
            if "Статус:" in field.name:
                embed.set_field_at(
                    i,
                    name="🔴 Статус:",
                    value="✅ Контракт завершен!",
                    inline=False
                )
                break
        
        # Убираем все кнопки
        await message.edit(embed=embed, view=None)
        
        # Отправляем сообщение в ветку
        if message.thread:
            await message.thread.send(
                f'✅ Контракт завершен! Завершил: {interaction.user.mention}'
            )
        
        await interaction.response.send_message(
            '✅ Контракт завершен!',
            ephemeral=True
        )


class ContractPublishModal(Modal):
    """Модальная форма для публикации контракта"""
    
    def __init__(self):
        super().__init__(title='🚀 Публикация контракта', timeout=None)
        self.config = ConfigManager()

    contract_name = TextInput(
        label='Название контракта',
        placeholder='Например: Бирюзовый док',
        max_length=100,
        required=True
    )
    
    reward = TextInput(
        label='Награда',
        placeholder='Например: $20.000 / 20 вексельок',
        max_length=100,
        required=True
    )
    
    duration_and_execution = TextInput(
        label='Срок действия / Длится',
        placeholder='Например: до 25.12.2024 / 2ч 30м',
        max_length=100,
        required=True
    )
    
    complete_and_chance = TextInput(
        label='Выполнить за / Шанс',
        placeholder='Например: от 4ч до 12ч / 100%',
        max_length=100,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        """Обработка отправки формы публикации контракта"""
        try:
            # Парсим награду (процент / вексели)
            reward_input = self.reward.value
            reward_parts = [part.strip() for part in reward_input.split('/')]
            
            if len(reward_parts) != 2:
                await interaction.response.send_message(
                    "❌ Неверный формат награды! Используйте: деньги / вексели\nНапример: $20.000 / 20 вексельок",
                    ephemeral=True
                )
                return
            
            reward_money = reward_parts[0]
            reward_amount = reward_parts[1]
            
            # Парсим первое объединенное поле (Срок / Длится)
            duration_input = self.duration_and_execution.value
            duration_parts = [part.strip() for part in duration_input.split('/')]
            
            if len(duration_parts) != 2:
                await interaction.response.send_message(
                    "❌ Неверный формат! Используйте: Срок действия / Длится\nНапример: до 25.12.2024 / 2ч 30м",
                    ephemeral=True
                )
                return
            
            contract_duration = duration_parts[0]
            execution_time = duration_parts[1]
            
            # Парсим второе объединенное поле (Выполнить / Шанс)
            complete_input = self.complete_and_chance.value
            complete_parts = [part.strip() for part in complete_input.split('/')]
            
            if len(complete_parts) != 2:
                await interaction.response.send_message(
                    "❌ Неверный формат! Используйте: Выполнить за / Шанс\nНапример: от 4ч до 12ч / 100%",
                    ephemeral=True
                )
                return
            
            complete_for = complete_parts[0]
            chance = complete_parts[1]
            
            # Получаем канал Members
            members_channel_id = self.config.get('contracts_members_channel_id', 0)
            if not members_channel_id:
                await interaction.response.send_message(
                    '❌ Канал Members не настроен!',
                    ephemeral=True
                )
                return
            
            members_channel = interaction.guild.get_channel(members_channel_id)
            if not members_channel:
                await interaction.response.send_message(
                    '❌ Канал не найден!',
                    ephemeral=True
                )
                return
            
            # Создаем красивый embed контракта В СТИЛЕ ПРИМЕРА
            embed = discord.Embed(
                color=0x2b2d31,  # Темно-серый цвет как в примере
                timestamp=datetime.now()
            )
            
            embed.title = f"📋 {self.contract_name.value}"
            
            # Основная информация
            embed.description = (
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"**👤 Создал:** {interaction.user.mention}\n"
                f"━━━━━━━━━━━━━━━━━━━━"
            )
            
            # Награда (первое поле)
            embed.add_field(
                name="💰 Награда:",
                value=f"{reward_money} / {reward_amount}",
                inline=False
            )
            
            # Информация о контракте
            embed.add_field(
                name="⏰ Срок действия контракта:",
                value=f"{contract_duration}",
                inline=False
            )
            
            embed.add_field(
                name="🕒 Контракт длится:",
                value=f"{execution_time}",
                inline=False
            )
            
            embed.add_field(
                name="⚡ Выполнить за:",
                value=f"{complete_for}",
                inline=False
            )
            
            embed.add_field(
                name="🎲 Шанс:",
                value=f"{chance}",
                inline=False
            )
            
            # Участники
            embed.add_field(
                name="📊 Участники:",
                value="❌ Пока нет участников",
                inline=False
            )
            
            # Статус
            embed.add_field(
                name="🟢 Статус:",
                value="✅ Открыта регистрация",
                inline=False
            )
            
            embed.set_footer(text='Price FamQ')
            
            # Получаем роли Family и Price Academy для упоминания
            family_role_id = self.config.get('family_role_id', 0)
            member_role_id = self.config.get('member_role_id', 0)
            
            role_mentions = []
            role_names = []
            
            # Проверяем и добавляем роль Family
            if family_role_id:
                family_role = interaction.guild.get_role(family_role_id)
                if family_role:
                    role_mentions.append(family_role.mention)
                    role_names.append(family_role.name)
                    print(f"✅ Роль Family найдена: {family_role.name} (ID: {family_role_id})")
                else:
                    print(f"❌ Роль Family с ID {family_role_id} не найдена на сервере")
            else:
                print("❌ ID роли Family не найден в конфиге")
            
            # Проверяем и добавляем роль Price Academy
            if member_role_id:
                member_role = interaction.guild.get_role(member_role_id)
                if member_role:
                    role_mentions.append(member_role.mention)
                    role_names.append(member_role.name)
                    print(f"✅ Роль Price Academy найдена: {member_role.name} (ID: {member_role_id})")
                else:
                    print(f"❌ Роль Price Academy с ID {member_role_id} не найдена на сервере")
            else:
                print("❌ ID роли Price Academy не найден в конфиге")
            
            # Объединяем упоминания и названия
            content = " ".join(role_mentions) + "\n\n" if role_mentions else ""
            role_name_text = " и ".join(role_names) if role_names else "не найдены"
            
            # Создаем View с кнопками (включая кнопку "Начать контракт")
            view = ContractView()
            
            # Отправляем контракт с кнопками
            message = await members_channel.send(content=content, embed=embed, view=view)
            
            # Сохраняем ссылку на сообщение в View
            view.message = message
            
            print(f"✅ Контракт создан в канале контрактов")
            print(f"✅ Content сообщения: {content}")
            
            # Создаем ветку для контракта
            try:
                thread = await message.create_thread(
                    name=f"🚀 {self.contract_name.value[:80]}",
                    auto_archive_duration=1440  # 24 часа
                )
                print(f"✅ Ветка создана для контракта {self.contract_name.value}")
            except Exception as e:
                print(f"❌ Ошибка создания ветки: {e}")
            
            await interaction.response.send_message(
                f"✅ Контракт \"{self.contract_name.value}\" успешно опубликован! Тегнуты роли: **{role_name_text}**",
                ephemeral=True
            )
            
        except Exception as e:
            print(f"❌ Ошибка при создании контракта: {e}")
            try:
                await interaction.response.send_message(
                    f"❌ Ошибка при создании контракта: {str(e)}",
                    ephemeral=True
                )
            except:
                try:
                    await interaction.followup.send(
                        f"❌ Ошибка при создании контракта: {str(e)}",
                        ephemeral=True
                    )
                except:
                    pass




class ContractCreateButton(View):
    """Кнопка для открытия формы создания контракта"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(
        label='📋 Создать контракт',
        style=discord.ButtonStyle.success,
        custom_id='contract_create_button'
    )
    async def create_button(self, interaction: discord.Interaction, button: Button):
        """Обработка нажатия кнопки создания контракта"""
        await interaction.response.send_modal(ContractPublishModal())


class Contracts(commands.Cog):
    """Модуль системы контрактов"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()
        self.pinned_message_id = None
        
        # Регистрируем персистентные View
        self.bot.add_view(ContractView())
        self.bot.add_view(ContractFinishView())
        
        # Запускаем таск автозакрепления
        self.auto_pin_task.start()
    
    def cog_unload(self):
        """Остановка таска при выгрузке модуля"""
        self.auto_pin_task.cancel()
    
    @tasks.loop(hours=3)
    async def auto_pin_task(self):
        """Автоматическое закрепление сообщения с кнопкой каждые 3 часа"""
        if not self.pinned_message_id:
            return
        
        contracts_channel_id = self.config.get('contracts_channel_id', 0)
        if not contracts_channel_id or not self.pinned_message_id:
            return
        
        channel = self.bot.get_channel(contracts_channel_id)
        if not channel:
            return
        
        try:
            message = await channel.fetch_message(self.pinned_message_id)
            # Проверяем, закреплено ли сообщение
            if not message.pinned:
                await message.pin()
                print(f"✅ Сообщение с кнопкой контракта закреплено в #{channel.name}")
        except discord.NotFound:
            print("⚠️ Сообщение с кнопкой контракта не найдено")
            self.pinned_message_id = None
        except discord.Forbidden:
            print("❌ Нет прав для закрепления сообщений")
        except Exception as e:
            print(f"❌ Ошибка при закреплении: {e}")
    
    @auto_pin_task.before_loop
    async def before_auto_pin(self):
        """Ждем пока бот будет готов"""
        await self.bot.wait_until_ready()
    
    @commands.command(name='contract')
    @commands.has_permissions(administrator=True)
    async def create_contract(self, ctx):
        """Открывает форму для создания контракта"""
        # Отправляем временное сообщение с кнопкой
        view = ContractCreateButton()
        msg = await ctx.send('Нажмите кнопку чтобы открыть форму контракта:', view=view)
        
        try:
            await ctx.message.delete()
        except:
            pass


async def setup(bot):
    """Функция загрузки cog"""
    await bot.add_cog(Contracts(bot))