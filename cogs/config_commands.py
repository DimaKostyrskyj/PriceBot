# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from utils.config_manager import ConfigManager

class ConfigCommands(commands.Cog):
    """Модуль команд настройки бота"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()
    
    @commands.command(name='config')
    @commands.has_permissions(administrator=True)
    async def configure(self, ctx, setting: str = None, value: str = None):
        """
        Настройка бота
        Использование: !config [setting] [value]
        """
        if not setting:
            # Показываем текущие настройки
            embed = discord.Embed(
                title='⚙️ Конфигурация бота Price FamQ',
                description='Текущие настройки:',
                color=self.config.get_color('primary')
            )
            
            # Каналы
            welcome_ch = self.config.get('welcome_channel_id')
            app_ch = self.config.get('application_channel_id')
            review_ch = self.config.get('review_channel_id')
            logs_ch = self.config.get('logs_channel_id')
            
            embed.add_field(
                name='📺 Каналы',
                value=f'**Приветствие:** {f"<#{welcome_ch}>" if welcome_ch else "Не настроен"}\n'
                      f'**Заявки:** {f"<#{app_ch}>" if app_ch else "Не настроен"}\n'
                      f'**Рассмотрение:** {f"<#{review_ch}>" if review_ch else "Не настроен"}\n'
                      f'**Логи:** {f"<#{logs_ch}>" if logs_ch else "Не настроен"}',
                inline=False
            )
            
            # Роли
            mod_roles = self.config.get('moderator_role_ids', [])
            member_role = self.config.get('member_role_id')
            auto_role = self.config.get('auto_role_id')
            dev_roles = self.config.get('dev_role_ids', [])
            owner_roles = self.config.get('owner_role_ids', [])
            
            mod_roles_text = ', '.join([f'<@&{r}>' for r in mod_roles]) if mod_roles else 'Не настроены'
            dev_roles_text = ', '.join([f'<@&{r}>' for r in dev_roles]) if dev_roles else 'Не настроены'
            owner_roles_text = ', '.join([f'<@&{r}>' for r in owner_roles]) if owner_roles else 'Не настроены'
            
            embed.add_field(
                name='🎭 Роли',
                value=f'**Рекруты (REC):** {mod_roles_text}\n'
                      f'**Участник (Family):** {f"<@&{member_role}>" if member_role else "Не настроена"}\n'
                      f'**Авто-роль (Guest):** {f"<@&{auto_role}>" if auto_role else "Не настроена"}\n'
                      f'**Developer:** {dev_roles_text}\n'
                      f'**Owner:** {owner_roles_text}',
                inline=False
            )
            
            # Логотип
            logo_url = self.config.get('logo_url')
            logo_status = '✅ Настроен' if logo_url != "https://i.imgur.com/your_logo.png" else '❌ Не настроен'
            embed.add_field(name='🎨 Логотип', value=logo_status, inline=False)
            
            # Команды
            embed.add_field(
                name='📝 Команды настройки',
                value='```\n'
                      '!config welcome_channel #канал или ID\n'
                      '!config application_channel #канал или ID\n'
                      '!config review_channel #канал или ID\n'
                      '!config logs_channel #канал или ID\n'
                      '!config moderator_role @роль или ID (REC)\n'
                      '!config member_role @роль или ID (Price Academy)\n'
                      '!config auto_role @роль или ID (Friends)\n'
                      '!config dev_role @роль или ID\n'
                      '!config owner_role @роль или ID\n'
                      '!config logo <URL>\n'
                      '```',
                inline=False
            )
            
            await ctx.send(embed=embed)
            return
        
        # Обработка настроек
        # Каналы - принимаем как упоминание, так и ID
        if setting == 'welcome_channel':
            if ctx.message.channel_mentions:
                channel_id = ctx.message.channel_mentions[0].id
                channel = ctx.message.channel_mentions[0]
            elif value and value.isdigit():
                channel_id = int(value)
                channel = self.bot.get_channel(channel_id)
            else:
                await ctx.send('❌ Укажите канал (#канал) или ID канала')
                return
            
            self.config.set('welcome_channel_id', channel_id)
            await ctx.send(f'✅ Канал приветствия установлен: {channel.mention if channel else f"ID: {channel_id}"}')
        
        elif setting == 'application_channel':
            if ctx.message.channel_mentions:
                channel_id = ctx.message.channel_mentions[0].id
                channel = ctx.message.channel_mentions[0]
            elif value and value.isdigit():
                channel_id = int(value)
                channel = self.bot.get_channel(channel_id)
            else:
                await ctx.send('❌ Укажите канал (#канал) или ID канала')
                return
            
            self.config.set('application_channel_id', channel_id)
            await ctx.send(f'✅ Канал заявок установлен: {channel.mention if channel else f"ID: {channel_id}"}')
        
        elif setting == 'review_channel':
            if ctx.message.channel_mentions:
                channel_id = ctx.message.channel_mentions[0].id
                channel = ctx.message.channel_mentions[0]
            elif value and value.isdigit():
                channel_id = int(value)
                channel = self.bot.get_channel(channel_id)
            else:
                await ctx.send('❌ Укажите канал (#канал) или ID канала')
                return
            
            self.config.set('review_channel_id', channel_id)
            await ctx.send(f'✅ Канал рассмотрения установлен: {channel.mention if channel else f"ID: {channel_id}"}')
        
        elif setting == 'logs_channel':
            if ctx.message.channel_mentions:
                channel_id = ctx.message.channel_mentions[0].id
                channel = ctx.message.channel_mentions[0]
            elif value and value.isdigit():
                channel_id = int(value)
                channel = self.bot.get_channel(channel_id)
            else:
                await ctx.send('❌ Укажите канал (#канал) или ID канала')
                return
            
            self.config.set('logs_channel_id', channel_id)
            await ctx.send(f'✅ Канал логов установлен: {channel.mention if channel else f"ID: {channel_id}"}')
        
        # Роли - принимаем как упоминание, так и ID
        elif setting == 'moderator_role':
            if ctx.message.role_mentions:
                role_id = ctx.message.role_mentions[0].id
                role = ctx.message.role_mentions[0]
            elif value and value.isdigit():
                role_id = int(value)
                role = ctx.guild.get_role(role_id)
            else:
                await ctx.send('❌ Укажите роль (@роль) или ID роли')
                return
            
            moderator_roles = self.config.get('moderator_role_ids', [])
            if role_id not in moderator_roles:
                moderator_roles.append(role_id)
                self.config.set('moderator_role_ids', moderator_roles)
            await ctx.send(f'✅ Роль модератора добавлена: {role.mention if role else f"ID: {role_id}"}')
        
        elif setting == 'member_role':
            if ctx.message.role_mentions:
                role_id = ctx.message.role_mentions[0].id
                role = ctx.message.role_mentions[0]
            elif value and value.isdigit():
                role_id = int(value)
                role = ctx.guild.get_role(role_id)
            else:
                await ctx.send('❌ Укажите роль (@роль) или ID роли')
                return
            
            self.config.set('member_role_id', role_id)
            await ctx.send(f'✅ Роль Price Academy установлена: {role.mention if role else f"ID: {role_id}"}')
        
        elif setting == 'auto_role':
            if ctx.message.role_mentions:
                role_id = ctx.message.role_mentions[0].id
                role = ctx.message.role_mentions[0]
            elif value and value.isdigit():
                role_id = int(value)
                role = ctx.guild.get_role(role_id)
            else:
                await ctx.send('❌ Укажите роль (@роль) или ID роли')
                return
            
            self.config.set('auto_role_id', role_id)
            await ctx.send(f'✅ Авто-роль Friends установлена: {role.mention if role else f"ID: {role_id}"}\nБудет выдаваться при входе на сервер.')
        
        elif setting == 'dev_role':
            if ctx.message.role_mentions:
                role_id = ctx.message.role_mentions[0].id
                role = ctx.message.role_mentions[0]
            elif value and value.isdigit():
                role_id = int(value)
                role = ctx.guild.get_role(role_id)
            else:
                await ctx.send('❌ Укажите роль (@роль) или ID роли')
                return
            
            dev_roles = self.config.get('dev_role_ids', [])
            if role_id not in dev_roles:
                dev_roles.append(role_id)
                self.config.set('dev_role_ids', dev_roles)
            await ctx.send(f'✅ Роль Dev добавлена: {role.mention if role else f"ID: {role_id}"}')
        
        elif setting == 'owner_role':
            if ctx.message.role_mentions:
                role_id = ctx.message.role_mentions[0].id
                role = ctx.message.role_mentions[0]
            elif value and value.isdigit():
                role_id = int(value)
                role = ctx.guild.get_role(role_id)
            else:
                await ctx.send('❌ Укажите роль (@роль) или ID роли')
                return
            
            owner_roles = self.config.get('owner_role_ids', [])
            if role_id not in owner_roles:
                owner_roles.append(role_id)
                self.config.set('owner_role_ids', owner_roles)
            await ctx.send(f'✅ Роль Owner добавлена: {role.mention if role else f"ID: {role_id}"}')
        
        elif setting == 'logo' and value:
            self.config.set('logo_url', value)
            await ctx.send(f'✅ Логотип обновлен!\n{value}')
        
        elif setting == 'remove_moderator' and ctx.message.role_mentions:
            moderator_roles = self.config.get('moderator_role_ids', [])
            role_id = ctx.message.role_mentions[0].id
            if role_id in moderator_roles:
                moderator_roles.remove(role_id)
                self.config.set('moderator_role_ids', moderator_roles)
                await ctx.send(f'✅ Роль модератора удалена: {ctx.message.role_mentions[0].mention}')
            else:
                await ctx.send(f'❌ Эта роль не является ролью модератора')
        
        elif setting == 'remove_dev' and ctx.message.role_mentions:
            dev_roles = self.config.get('dev_role_ids', [])
            role_id = ctx.message.role_mentions[0].id
            if role_id in dev_roles:
                dev_roles.remove(role_id)
                self.config.set('dev_role_ids', dev_roles)
                await ctx.send(f'✅ Роль Dev удалена: {ctx.message.role_mentions[0].mention}')
            else:
                await ctx.send(f'❌ Эта роль не является ролью Dev')
        
        elif setting == 'remove_owner' and ctx.message.role_mentions:
            owner_roles = self.config.get('owner_role_ids', [])
            role_id = ctx.message.role_mentions[0].id
            if role_id in owner_roles:
                owner_roles.remove(role_id)
                self.config.set('owner_role_ids', owner_roles)
                await ctx.send(f'✅ Роль Owner удалена: {ctx.message.role_mentions[0].mention}')
            else:
                await ctx.send(f'❌ Эта роль не является ролью Owner')
        
        else:
            await ctx.send('❌ Неверный формат команды. Используйте `!config` без параметров для справки.')
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Показать список команд"""
        embed = discord.Embed(
            title='📚 Команды бота Price FamQ',
            description='Список доступных команд',
            color=self.config.get_color('info')
        )
        
        # Команды для администраторов
        admin_commands = [
            '`!config` - Настройка бота',
            '`!setup_application` - Создать кнопку заявки',
            '`!reload` - Перезагрузить конфигурацию'
        ]
        embed.add_field(
            name='👑 Команды администратора',
            value='\n'.join(admin_commands),
            inline=False
        )
        
        # Команды для Dev/Owner
        if any(role.id in self.config.get('dev_role_ids', []) + self.config.get('owner_role_ids', []) 
               for role in ctx.author.roles):
            dev_commands = [
                '`!download_logs [дни]` - Скачать логи',
                '`!logs_stats` - Статистика логов',
                '`!clear_logs` - Очистить логи (Owner)'
            ]
            embed.add_field(
                name='🛠️ Команды Dev/Owner',
                value='\n'.join(dev_commands),
                inline=False
            )
        
        # Информация
        embed.add_field(
            name='ℹ️ Информация',
            value='Для подробной настройки используйте `!config` без параметров',
            inline=False
        )
        
        embed.set_footer(text='Price FamQ • GTA 5 RP')
        
        await ctx.send(embed=embed)
    
    @commands.command(name='reload')
    @commands.has_permissions(administrator=True)
    async def reload_config(self, ctx):
        """Перезагрузить конфигурацию"""
        try:
            self.config.reload()
            
            # Перезагружаем конфигурацию во всех cog
            for cog in self.bot.cogs.values():
                if hasattr(cog, 'config'):
                    cog.config.reload()
            
            embed = discord.Embed(
                title='🔄 Конфигурация перезагружена',
                description='Все настройки были обновлены из config.json',
                color=self.config.get_color('success')
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f'❌ Ошибка при перезагрузке: {e}')
    
    @commands.command(name='status')
    async def status(self, ctx):
        """Показать статус бота"""
        embed = discord.Embed(
            title='📊 Статус бота Price FamQ',
            color=self.config.get_color('primary')
        )
        
        # Информация о боте
        embed.add_field(name='🤖 Бот', value=self.bot.user.name, inline=True)
        embed.add_field(name='🆔 ID', value=self.bot.user.id, inline=True)
        embed.add_field(name='📡 Пинг', value=f'{round(self.bot.latency * 1000)}ms', inline=True)
        
        # Статистика сервера
        guild = ctx.guild
        embed.add_field(name='👥 Участников', value=len(guild.members), inline=True)
        embed.add_field(name='📺 Каналов', value=len(guild.channels), inline=True)
        embed.add_field(name='🎭 Ролей', value=len(guild.roles), inline=True)
        
        # Модули
        modules = len(self.bot.cogs)
        embed.add_field(name='📦 Загружено модулей', value=modules, inline=True)
        
        logo_url = self.config.get('logo_url')
        if logo_url != "https://i.imgur.com/your_logo.png":
            embed.set_thumbnail(url=logo_url)
        
        embed.set_footer(text='Price FamQ • GTA 5 RP')
        
        await ctx.send(embed=embed)
    
    @commands.command(name='test')
    @commands.has_permissions(administrator=True)
    async def test_config(self, ctx):
        """Тестирование всех настроек бота"""
        embed = discord.Embed(
            title='🧪 Тест конфигурации бота',
            description='Проверка всех настроек и функций',
            color=self.config.get_color('info')
        )
        
        results = []
        
        # Проверка каналов
        welcome_ch = self.config.get('welcome_channel_id')
        app_ch = self.config.get('application_channel_id')
        review_ch = self.config.get('review_channel_id')
        logs_ch = self.config.get('logs_channel_id')
        
        # Тест канала приветствия
        if welcome_ch and self.bot.get_channel(welcome_ch):
            results.append('✅ Канал приветствия настроен и доступен')
            try:
                channel = self.bot.get_channel(welcome_ch)
                test_embed = discord.Embed(
                    title='🧪 Тестовое сообщение',
                    description='Это тестовое приветствие для проверки работы бота',
                    color=self.config.get_color('primary')
                )
                await channel.send(embed=test_embed)
                results.append('  └ Отправка сообщений работает')
            except discord.Forbidden:
                results.append('  └ ❌ Нет прав на отправку сообщений')
        else:
            results.append('❌ Канал приветствия не настроен или недоступен')
        
        # Тест канала заявок
        if app_ch and self.bot.get_channel(app_ch):
            results.append('✅ Канал заявок настроен и доступен')
            try:
                channel = self.bot.get_channel(app_ch)
                permissions = channel.permissions_for(ctx.guild.me)
                if permissions.send_messages and permissions.embed_links:
                    results.append('  └ Права на отправку сообщений есть')
                else:
                    results.append('  └ ❌ Недостаточно прав')
            except:
                results.append('  └ ❌ Ошибка проверки прав')
        else:
            results.append('❌ Канал заявок не настроен или недоступен')
        
        # Тест канала рассмотрения
        if review_ch and self.bot.get_channel(review_ch):
            results.append('✅ Канал рассмотрения настроен и доступен')
        else:
            results.append('❌ Канал рассмотрения не настроен или недоступен')
        
        # Тест канала логов
        if logs_ch and self.bot.get_channel(logs_ch):
            results.append('✅ Канал логов настроен и доступен')
            try:
                channel = self.bot.get_channel(logs_ch)
                test_log = discord.Embed(
                    title='🧪 Тестовый лог',
                    description='Проверка работы системы логирования',
                    color=self.config.get_color('info')
                )
                await channel.send(embed=test_log)
                results.append('  └ Логирование работает')
            except discord.Forbidden:
                results.append('  └ ❌ Нет прав на отправку логов')
        else:
            results.append('❌ Канал логов не настроен или недоступен')
        
        # Проверка ролей
        mod_roles = self.config.get('moderator_role_ids', [])
        member_role = self.config.get('member_role_id')
        dev_roles = self.config.get('dev_role_ids', [])
        owner_roles = self.config.get('owner_role_ids', [])
        
        if mod_roles:
            valid_mod_roles = [r for r in mod_roles if ctx.guild.get_role(r)]
            results.append(f'✅ Роли модераторов: {len(valid_mod_roles)}/{len(mod_roles)} доступны')
        else:
            results.append('❌ Роли модераторов не настроены')
        
        if member_role and ctx.guild.get_role(member_role):
            results.append('✅ Роль участника настроена и доступна')
            # Проверка иерархии ролей
            bot_top_role = ctx.guild.me.top_role
            member_role_obj = ctx.guild.get_role(member_role)
            if bot_top_role > member_role_obj:
                results.append('  └ Иерархия ролей правильная')
            else:
                results.append('  └ ⚠️ Роль бота должна быть выше роли участника!')
        else:
            results.append('❌ Роль участника не настроена или недоступна')
        
        if dev_roles:
            valid_dev_roles = [r for r in dev_roles if ctx.guild.get_role(r)]
            results.append(f'✅ Роли Dev: {len(valid_dev_roles)}/{len(dev_roles)} доступны')
        else:
            results.append('⚠️ Роли Dev не настроены')
        
        if owner_roles:
            valid_owner_roles = [r for r in owner_roles if ctx.guild.get_role(r)]
            results.append(f'✅ Роли Owner: {len(valid_owner_roles)}/{len(owner_roles)} доступны')
        else:
            results.append('⚠️ Роли Owner не настроены')
        
        # Проверка логотипа
        logo_url = self.config.get('logo_url')
        if logo_url and logo_url != "https://i.imgur.com/your_logo.png":
            results.append('✅ Логотип настроен')
        else:
            results.append('⚠️ Логотип не настроен (используется по умолчанию)')
        
        # Проверка модулей
        cogs_status = []
        if 'Welcome' in self.bot.cogs:
            cogs_status.append('✅ Приветствие')
        if 'Applications' in self.bot.cogs:
            cogs_status.append('✅ Заявки')
        if 'Logs' in self.bot.cogs:
            cogs_status.append('✅ Логирование')
        if 'ConfigCommands' in self.bot.cogs:
            cogs_status.append('✅ Настройка')
        
        results.append(f'\n📦 Модули: {len(cogs_status)}/4 загружены')
        results.extend(['  └ ' + status for status in cogs_status])
        
        # Проверка прав бота
        bot_permissions = ctx.guild.me.guild_permissions
        perms_check = []
        if bot_permissions.send_messages:
            perms_check.append('✅ Send Messages')
        if bot_permissions.embed_links:
            perms_check.append('✅ Embed Links')
        if bot_permissions.manage_roles:
            perms_check.append('✅ Manage Roles')
        else:
            perms_check.append('❌ Manage Roles (нужно!)')
        if bot_permissions.read_message_history:
            perms_check.append('✅ Read Message History')
        
        results.append('\n🔐 Права бота:')
        results.extend(['  └ ' + perm for perm in perms_check])
        
        # Итоговый результат
        embed.description = '\n'.join(results)
        
        # Подсчет проблем
        errors = len([r for r in results if r.startswith('❌')])
        warnings = len([r for r in results if r.startswith('⚠️')])
        
        if errors == 0 and warnings == 0:
            embed.color = self.config.get_color('success')
            embed.add_field(
                name='✅ Итог',
                value='Все настройки корректны! Бот готов к работе.',
                inline=False
            )
        elif errors > 0:
            embed.color = self.config.get_color('error')
            embed.add_field(
                name='❌ Итог',
                value=f'Найдено ошибок: {errors}, предупреждений: {warnings}\nИсправьте ошибки для корректной работы.',
                inline=False
            )
        else:
            embed.color = self.config.get_color('warning')
            embed.add_field(
                name='⚠️ Итог',
                value=f'Предупреждений: {warnings}\nБот работает, но есть рекомендации.',
                inline=False
            )
        
        embed.set_footer(text='Price FamQ • Тест конфигурации')
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Функция загрузки cog"""
    await bot.add_cog(ConfigCommands(bot))