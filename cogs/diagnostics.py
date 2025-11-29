# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from utils.config_manager import ConfigManager

class Diagnostics(commands.Cog):
    """Модуль диагностики бота"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Отладка сообщений"""
        if message.author.bot:
            return
        
        # Логируем ВСЕ сообщения с префиксом
        if message.content.startswith('!'):
            print("=" * 50)
            print(f"📝 ПОЛУЧЕНО СООБЩЕНИЕ С ПРЕФИКСОМ:")
            print(f"   Текст: {message.content}")
            print(f"   Автор: {message.author} (ID: {message.author.id})")
            print(f"   Канал: {message.channel} (ID: {message.channel.id})")
            print(f"   Гильдия: {message.guild}")
            print(f"   Префикс бота: {self.bot.command_prefix}")
            print(f"   Всего команд загружено: {len(self.bot.commands)}")
            print("=" * 50)
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Когда команда распознана"""
        print(f"✅ КОМАНДА РАСПОЗНАНА: {ctx.command.name}")
        print(f"   Автор: {ctx.author}")
        print(f"   Канал: {ctx.channel}")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Когда команда вызвала ошибку"""
        print(f"❌ ОШИБКА КОМАНДЫ: {ctx.command}")
        print(f"   Ошибка: {error}")
        print(f"   Тип: {type(error)}")
        
        # Отправляем пользователю
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f'❌ Команда не найдена! Используйте `!list_commands` для списка команд.')
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f'❌ У вас нет прав для этой команды!')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'❌ Не хватает аргументов! Используйте `!commands` для помощи.')
        else:
            await ctx.send(f'❌ Ошибка: {error}')
    
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Когда команда успешно выполнена"""
        print(f"✅ КОМАНДА ВЫПОЛНЕНА: {ctx.command.name}")
        print(f"   Автор: {ctx.author}")
        print(f"   Канал: {ctx.channel}")
    
    @commands.command(name='test_ping')
    async def test_ping(self, ctx):
        """Тестовая команда для проверки работы"""
        await ctx.send('🏓 Понг! Команды работают!')
    
    @commands.command(name='debug')
    async def debug_info(self, ctx):
        """Показать отладочную информацию"""
        embed = discord.Embed(
            title='🔍 Диагностика бота',
            color=0x5865F2
        )
        
        # Информация о боте
        embed.add_field(
            name='Бот',
            value=f'**Имя:** {self.bot.user.name}\n**ID:** {self.bot.user.id}',
            inline=False
        )
        
        # Префикс
        embed.add_field(
            name='Префикс',
            value=f'`{self.bot.command_prefix}`',
            inline=True
        )
        
        # Загруженные команды
        commands_list = [cmd.name for cmd in self.bot.commands]
        embed.add_field(
            name=f'Команды ({len(commands_list)})',
            value=', '.join([f'`{cmd}`' for cmd in commands_list[:10]]) + ('...' if len(commands_list) > 10 else ''),
            inline=False
        )
        
        # Загруженные cogs
        cogs_list = list(self.bot.cogs.keys())
        embed.add_field(
            name=f'Модули ({len(cogs_list)})',
            value='\n'.join([f'✅ {cog}' for cog in cogs_list]),
            inline=False
        )
        
        # Intents
        embed.add_field(
            name='Intents',
            value=f'Messages: {self.bot.intents.message_content}\n'
                  f'Members: {self.bot.intents.members}\n'
                  f'Guilds: {self.bot.intents.guilds}',
            inline=False
        )
        
        # Права бота
        bot_member = ctx.guild.get_member(self.bot.user.id)
        perms = bot_member.guild_permissions
        
        embed.add_field(
            name='Права',
            value=f'Administrator: {perms.administrator}\n'
                  f'Manage Roles: {perms.manage_roles}\n'
                  f'Manage Channels: {perms.manage_channels}\n'
                  f'Send Messages: {perms.send_messages}',
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='list_commands')
    async def list_all_commands(self, ctx):
        """Список всех команд"""
        commands_by_cog = {}
        
        for command in self.bot.commands:
            cog_name = command.cog_name or 'Без модуля'
            if cog_name not in commands_by_cog:
                commands_by_cog[cog_name] = []
            commands_by_cog[cog_name].append(command.name)
        
        embed = discord.Embed(
            title='📋 Все команды бота',
            description=f'Префикс: `{self.bot.command_prefix}`',
            color=0x43B581
        )
        
        for cog_name, commands in commands_by_cog.items():
            embed.add_field(
                name=f'**{cog_name}** ({len(commands)})',
                value=', '.join([f'`!{cmd}`' for cmd in commands]),
                inline=False
            )
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Diagnostics(bot))