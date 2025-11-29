# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from utils.config_manager import ConfigManager

class Help(commands.Cog):
    """Модуль помощи"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()
    
    @commands.command(name='commands', aliases=['помощь'])
    async def help_command(self, ctx):
        """Показывает список всех команд бота"""
        
        embed = discord.Embed(
            title='📚 Справка по командам Price FamQ Bot',
            description='Все доступные команды для управления ботом',
            color=self.config.get_color('info')
        )
        
        
        # Настройка
        embed.add_field(
            name='⚙️ Настройка (только администраторы)',
            value=(
                '`!config` - Показать все настройки\n'
                '`!config welcome_channel #канал` - Канал приветствий\n'
                '`!config application_channel #канал` - Канал заявок\n'
                '`!config review_channel #канал` - Канал рассмотрения\n'
                '`!config logs_channel #канал` - Канал логов\n'
                '`!config contracts_channel #канал` - Канал запросов контрактов\n'
                '`!config contracts_members_channel #канал` - Канал контрактов Members\n'
                '`!config moderator_role @роль` - Роль модераторов (REC)\n'
                '`!config member_role @роль` - Роль участников (Price Academy)\n'
                '`!config auto_role @роль` - Авто-роль при входе (Friends)\n'
                '`!config dev_role @роль` - Роль разработчиков\n'
                '`!config owner_role @роль` - Роль владельцев\n'
                '`!config logo <URL>` - Логотип бота'
            ),
            inline=False
        )
        
        # Заявки
        embed.add_field(
            name='📝 Заявки',
            value=(
                '`!setup_application` - Создать кнопку подачи заявки\n'
                '**Кнопка "Подать заявку"** - Открыть форму заявки\n'
                '**Кнопка "Одобрить"** - Одобрить заявку (только REC)\n'
                '**Кнопка "Отклонить"** - Отклонить заявку (только REC)'
            ),
            inline=False
        )
        
        # Контракты
        embed.add_field(
            name='📋 Контракты (администраторы)',
            value=(
                '`!setup_contract_request` - Создать фиксированную кнопку запроса\n'
                '`!setup_contract_info` - Отправить инфо в Members канал\n'
                '`!contract` - Создать контракт (форма)\n'
                '`!publish_contract "название" "срок" "время" "за сколько" "%"` - Опубликовать контракт (старый способ)'
            ),
            inline=False
        )
        
        # Тестирование
        embed.add_field(
            name='🧪 Тестирование (администраторы)',
            value=(
                '`!test` - Проверить все настройки бота\n'
                '`!test welcome` - Тест приветствия\n'
                '`!test application` - Тест заявки\n'
                '`!test roles` - Тест ролей\n'
                '`!test channels` - Тест каналов\n'
                '`!test all` - Полный тест'
            ),
            inline=False
        )
        
        # Утилиты
        embed.add_field(
            name='🔧 Утилиты',
            value=(
                '`!commands` - Показать это сообщение\n'
                '`!ping` - Проверить задержку бота'
            ),
            inline=False
        )
        
        # Информация
        embed.add_field(
            name='ℹ️ Информация',
            value=(
                '**Префикс команд:** `!`\n'
                '**Версия бота:** 2.1\n'
                '**Модули:** Приветствие, Заявки, Контракты, Логи, Настройка'
            ),
            inline=False
        )
        
        embed.set_footer(
            text='Price FamQ Bot • Создан для Price FamQ',
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='ping')
    async def ping_command(self, ctx):
        """Показывает задержку бота"""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title='🏓 Понг!',
            description=f'Задержка: **{latency}ms**',
            color=self.config.get_color('success') if latency < 100 else self.config.get_color('warning')
        )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Функция загрузки cog"""
    await bot.add_cog(Help(bot))