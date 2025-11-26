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
        
        # Создание минималистичного embed приветствия
        embed = discord.Embed(
            description=f'### Добро пожаловать, {member.mention}\n\nМы рады видеть тебя в **Price FamQ**',
            color=self.config.get_color('primary'),
            timestamp=datetime.now()
        )
        
        # Установка логотипа
        logo_url = self.config.get('logo_url')
        if logo_url and logo_url != "https://i.imgur.com/your_logo.png":
            embed.set_thumbnail(url=logo_url)
        
        # Основная информация
        embed.add_field(
            name='',
            value=f'**Хочешь стать частью семьи?**\nПодай заявку в <#{self.config.get("application_channel_id")}>',
            inline=False
        )
        
        # Футер
        embed.set_footer(
            text=f'Участник #{len(member.guild.members)} • Price FamQ',
            icon_url=member.display_avatar.url
        )
        
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