# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from datetime import datetime
from utils.config_manager import ConfigManager

class Welcome(commands.Cog):
    """Модуль приветствия новых участников"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Приветствие нового участника"""
        welcome_channel_id = self.config.get('welcome_channel_id')
        
        # Автоматическая выдача роли Friends
        auto_role_id = self.config.get('auto_role_id')
        if auto_role_id:
            auto_role = member.guild.get_role(auto_role_id)
            if auto_role:
                try:
                    await member.add_roles(auto_role)
                    print(f"✅ Роль Friends выдана пользователю {member.name}")
                except discord.Forbidden:
                    print(f"❌ Нет прав для выдачи роли Friends")
                except Exception as e:
                    print(f"❌ Ошибка при выдаче роли: {e}")
        
        if not welcome_channel_id:
            return
        
        welcome_channel = self.bot.get_channel(welcome_channel_id)
        
        if not welcome_channel:
            print(f"Warning: Welcome channel {welcome_channel_id} not found")
            return
        
        # Создание красивого embed приветствия
        embed = discord.Embed(
            color=self.config.get_color('primary')
        )
        
        # Красивое описание с эмодзи и форматированием
        welcome_text = (
            f"## 👋 Добро пожаловать, {member.mention}!\n\n"
            f"✨ **Мы рады приветствовать тебя в Price FamQ!**\n\n"
            f"Теперь ты носишь роль **Friends** и можешь начать свой путь в нашей семье.\n\n"
            f"╭─────────────────────╮\n"
            f"│  **📝 Хочешь вступить в семью?**  │\n"
            f"╰─────────────────────╯\n\n"
            f"Подай заявку в <#{self.config.get('application_channel_id')}> и стань частью **Price Academy**!"
        )
        
        embed.description = welcome_text
        
        # Установка аватара пользователя как большую картинку
        embed.set_image(url=member.display_avatar.url)
        
        # Установка логотипа
        
        # Информационные поля
        embed.add_field(
            name='🎮 Участник',
            value=f'**#{len(member.guild.members)}**',
            inline=True
        )
        
        embed.add_field(
            name='📅 Присоединился',
            value=f'{datetime.now().strftime("%d.%m.%Y")}',
            inline=True
        )
        
        embed.add_field(
            name='🎭 Роль',
            value='**Friends**',
            inline=True
        )
        
        # Красивый футер
        embed.set_footer(text='Price FamQ')
        
        embed.timestamp = datetime.now()
        
        try:
            await welcome_channel.send(embed=embed)
            print(f"✅ Отправлено приветствие для {member.name}")
        except discord.Forbidden:
            print(f"❌ Нет прав для отправки в канал приветствия")
        except Exception as e:
            print(f"❌ Ошибка при отправке приветствия: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Логирование выхода участника"""
        logs_channel_id = self.config.get('logs_channel_id')
        
        if not logs_channel_id:
            return
        
        logs_channel = self.bot.get_channel(logs_channel_id)
        
        if not logs_channel:
            return
        
        embed = discord.Embed(
            title='👋 Участник покинул сервер',
            description=f'{member.mention} ({member.name})',
            color=self.config.get_color('warning'),
            timestamp=datetime.now()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name='ID', value=member.id, inline=True)
        embed.add_field(name='Аккаунт создан', value=member.created_at.strftime('%d.%m.%Y'), inline=True)
        
        try:
            await logs_channel.send(embed=embed)
        except:
            pass

async def setup(bot):
    """Функция загрузки cog"""
    await bot.add_cog(Welcome(bot))