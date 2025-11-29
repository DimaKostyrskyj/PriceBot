# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from utils.config_manager import ConfigManager
from utils.permissions import permissions

class ConfigCommands(commands.Cog):
    """Модуль команд настройки бота"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()
    
    def check_permissions(self, ctx):
        """Проверка прав доступа к команде config"""
        return permissions.can_use_config(ctx.author)
    
    @commands.command(name='roles')
    async def manage_roles(self, ctx, action: str = None, role_type: str = None, value: str = None):
        """
        Управление ролями бота
        !roles - показать все роли
        !roles add owner @роль - добавить роль Owner
        !roles remove owner @роль - удалить роль Owner
        !roles clear owner - очистить все роли Owner
        """
        # Проверка прав
        if not self.check_permissions(ctx):
            embed = discord.Embed(
                title='❌ Нет доступа',
                description='У вас нет прав для использования этой команды!\n\n'
                           '**Требуется роль:** Owner или Developer',
                color=self.config.get_color('error')
            )
            await ctx.send(embed=embed)
            return
        
        # Показать все роли
        if not action:
            await self.show_all_roles(ctx)
            return
        
        # Добавить роль
        if action == 'add':
            if not role_type or not value:
                await ctx.send("❌ Использование: `!roles add <тип_роли> @роль`")
                return
            await self.add_role(ctx, role_type, value)
        
        # Удалить роль
        elif action == 'remove':
            if not role_type or not value:
                await ctx.send("❌ Использование: `!roles remove <тип_роли> @роль`")
                return
            await self.remove_role(ctx, role_type, value)
        
        # Очистить все роли
        elif action == 'clear':
            if not role_type:
                await ctx.send("❌ Использование: `!roles clear <тип_роли>`")
                return
            await self.clear_roles(ctx, role_type)
        
        else:
            await ctx.send(f"❌ Неизвестное действие: `{action}`\n"
                          f"Доступные действия: `add`, `remove`, `clear`")
    
    async def show_all_roles(self, ctx):
        """Показать все настроенные роли"""
        embed = discord.Embed(
            title='🎭 Настроенные роли',
            description='Все роли бота и их участники',
            color=0x2b2d31,
            timestamp=discord.utils.utcnow()
        )
        
        def format_roles(role_ids):
            if not role_ids:
                return "`Не настроены`"
            roles = []
            for role_id in role_ids:
                role = ctx.guild.get_role(role_id)
                if role:
                    roles.append(f"{role.mention} ({len(role.members)} чел.)")
                else:
                    roles.append(f"`ID: {role_id}` (не найдена)")
            return "\n".join(roles)
        
        def format_single_role(role_id):
            if not role_id:
                return "`Не настроена`"
            role = ctx.guild.get_role(role_id)
            if role:
                return f"{role.mention} ({len(role.members)} чел.)"
            return f"`ID: {role_id}` (не найдена)"
        
        # Администрация
        owner_roles = self.config.get('owner_role_ids', [])
        dep_owner_roles = self.config.get('dep_owner_role_ids', [])
        dev_roles = self.config.get('dev_role_ids', [])
        
        admin_text = (
            f"**Owner:**\n{format_roles(owner_roles)}\n\n"
            f"**Dep.Owner:**\n{format_roles(dep_owner_roles)}\n\n"
            f"**Developer:**\n{format_roles(dev_roles)}"
        )
        
        embed.add_field(
            name="👑 Администрация",
            value=admin_text,
            inline=False
        )
        
        # Модераторы
        contract_role = self.config.get('contract_role_id')
        mod_roles = self.config.get('moderator_role_ids', [])
        
        mod_text = (
            f"**Contract:**\n{format_single_role(contract_role)}\n\n"
            f"**REC:**\n{format_roles(mod_roles)}"
        )
        
        embed.add_field(
            name="👥 Модераторы",
            value=mod_text,
            inline=False
        )
        
        # Участники
        family_role = self.config.get('family_role_id')
        member_role = self.config.get('member_role_id')
        auto_role = self.config.get('auto_role_id')
        
        member_text = (
            f"**Family:**\n{format_single_role(family_role)}\n\n"
            f"**Price Academy:**\n{format_single_role(member_role)}\n\n"
            f"**Guest (авто):**\n{format_single_role(auto_role)}"
        )
        
        embed.add_field(
            name="🎮 Участники",
            value=member_text,
            inline=False
        )
        
        # Команды управления
        embed.add_field(
            name="📝 Команды",
            value=(
                "`!roles add owner @роль` - Добавить\n"
                "`!roles remove owner @роль` - Удалить\n"
                "`!roles clear owner` - Очистить все"
            ),
            inline=False
        )
        
        embed.set_footer(text=f"Запросил: {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    async def add_role(self, ctx, role_type: str, value: str):
        """Добавить роль"""
        role_id = self.parse_role(value, ctx)
        if not role_id:
            await ctx.send("❌ Роль не найдена!")
            return
        
        role = ctx.guild.get_role(role_id)
        role_mention = role.mention if role else f"`ID: {role_id}`"
        
        # Множественные роли
        if role_type in ['owner', 'owners']:
            current = self.config.get('owner_role_ids', [])
            if role_id in current:
                await ctx.send(f"⚠️ Роль {role_mention} уже добавлена как Owner")
                return
            current.append(role_id)
            self.config.set('owner_role_ids', current)
            await ctx.send(f"✅ Роль Owner добавлена: {role_mention}")
        
        elif role_type in ['dep_owner', 'depowner', 'dep']:
            current = self.config.get('dep_owner_role_ids', [])
            if role_id in current:
                await ctx.send(f"⚠️ Роль {role_mention} уже добавлена как Dep.Owner")
                return
            current.append(role_id)
            self.config.set('dep_owner_role_ids', current)
            await ctx.send(f"✅ Роль Dep.Owner добавлена: {role_mention}")
        
        elif role_type in ['developer', 'dev']:
            current = self.config.get('dev_role_ids', [])
            if role_id in current:
                await ctx.send(f"⚠️ Роль {role_mention} уже добавлена как Developer")
                return
            current.append(role_id)
            self.config.set('dev_role_ids', current)
            await ctx.send(f"✅ Роль Developer добавлена: {role_mention}")
        
        elif role_type in ['moderator', 'mod', 'rec']:
            current = self.config.get('moderator_role_ids', [])
            if role_id in current:
                await ctx.send(f"⚠️ Роль {role_mention} уже добавлена как REC")
                return
            current.append(role_id)
            self.config.set('moderator_role_ids', current)
            await ctx.send(f"✅ Роль REC добавлена: {role_mention}")
        
        # Одиночные роли
        elif role_type in ['contract']:
            self.config.set('contract_role_id', role_id)
            await ctx.send(f"✅ Роль Contract установлена: {role_mention}")
        
        elif role_type in ['family']:
            self.config.set('family_role_id', role_id)
            await ctx.send(f"✅ Роль Family установлена: {role_mention}")
        
        elif role_type in ['member', 'academy']:
            self.config.set('member_role_id', role_id)
            await ctx.send(f"✅ Роль Price Academy установлена: {role_mention}")
        
        elif role_type in ['auto', 'guest']:
            self.config.set('auto_role_id', role_id)
            await ctx.send(f"✅ Авто-роль Guest установлена: {role_mention}")
        
        else:
            await ctx.send(f"❌ Неизвестный тип роли: `{role_type}`\n\n"
                          f"Доступные типы: owner, dep_owner, dev, contract, rec, family, member, auto")
    
    async def remove_role(self, ctx, role_type: str, value: str):
        """Удалить роль"""
        role_id = self.parse_role(value, ctx)
        if not role_id:
            await ctx.send("❌ Роль не найдена!")
            return
        
        role = ctx.guild.get_role(role_id)
        role_mention = role.mention if role else f"`ID: {role_id}`"
        
        # Множественные роли
        if role_type in ['owner', 'owners']:
            current = self.config.get('owner_role_ids', [])
            if role_id not in current:
                await ctx.send(f"⚠️ Роль {role_mention} не найдена в списке Owner")
                return
            current.remove(role_id)
            self.config.set('owner_role_ids', current)
            await ctx.send(f"✅ Роль Owner удалена: {role_mention}")
        
        elif role_type in ['dep_owner', 'depowner', 'dep']:
            current = self.config.get('dep_owner_role_ids', [])
            if role_id not in current:
                await ctx.send(f"⚠️ Роль {role_mention} не найдена в списке Dep.Owner")
                return
            current.remove(role_id)
            self.config.set('dep_owner_role_ids', current)
            await ctx.send(f"✅ Роль Dep.Owner удалена: {role_mention}")
        
        elif role_type in ['developer', 'dev']:
            current = self.config.get('dev_role_ids', [])
            if role_id not in current:
                await ctx.send(f"⚠️ Роль {role_mention} не найдена в списке Developer")
                return
            current.remove(role_id)
            self.config.set('dev_role_ids', current)
            await ctx.send(f"✅ Роль Developer удалена: {role_mention}")
        
        elif role_type in ['moderator', 'mod', 'rec']:
            current = self.config.get('moderator_role_ids', [])
            if role_id not in current:
                await ctx.send(f"⚠️ Роль {role_mention} не найдена в списке REC")
                return
            current.remove(role_id)
            self.config.set('moderator_role_ids', current)
            await ctx.send(f"✅ Роль REC удалена: {role_mention}")
        
        else:
            await ctx.send(f"❌ Для одиночных ролей используйте `!roles clear {role_type}`")
    
    async def clear_roles(self, ctx, role_type: str):
        """Очистить все роли типа"""
        
        if role_type in ['owner', 'owners']:
            self.config.set('owner_role_ids', [])
            await ctx.send(f"✅ Все роли Owner очищены!")
        
        elif role_type in ['dep_owner', 'depowner', 'dep']:
            self.config.set('dep_owner_role_ids', [])
            await ctx.send(f"✅ Все роли Dep.Owner очищены!")
        
        elif role_type in ['developer', 'dev']:
            self.config.set('dev_role_ids', [])
            await ctx.send(f"✅ Все роли Developer очищены!")
        
        elif role_type in ['moderator', 'mod', 'rec']:
            self.config.set('moderator_role_ids', [])
            await ctx.send(f"✅ Все роли REC очищены!")
        
        elif role_type in ['contract']:
            self.config.set('contract_role_id', 0)
            await ctx.send(f"✅ Роль Contract очищена!")
        
        elif role_type in ['family']:
            self.config.set('family_role_id', 0)
            await ctx.send(f"✅ Роль Family очищена!")
        
        elif role_type in ['member', 'academy']:
            self.config.set('member_role_id', 0)
            await ctx.send(f"✅ Роль Price Academy очищена!")
        
        elif role_type in ['auto', 'guest']:
            self.config.set('auto_role_id', 0)
            await ctx.send(f"✅ Авто-роль Guest очищена!")
        
        else:
            await ctx.send(f"❌ Неизвестный тип роли: `{role_type}`")
    
    @commands.command(name='config')
    async def configure(self, ctx, setting: str = None, value: str = None):
        """
        Настройка бота (только для Owner и Developer)
        Использование: !config [setting] [value]
        """
        # Проверка прав
        if not self.check_permissions(ctx):
            embed = discord.Embed(
                title='❌ Нет доступа',
                description='У вас нет прав для использования этой команды!\n\n'
                           '**Требуется роль:** Owner или Developer',
                color=self.config.get_color('error')
            )
            await ctx.send(embed=embed)
            return
        
        if not setting:
            # Показываем красивые настройки с таблицей прав
            await self.show_config(ctx)
            return
        
        # Обработка настройки
        await self.update_setting(ctx, setting, value)
    
    async def show_config(self, ctx):
        """Показать текущую конфигурацию с таблицей прав"""
        
        # Первый embed - Настройки
        embed1 = discord.Embed(
            title='⚙️ Конфигурация Price FamQ Bot',
            description='**Текущие настройки системы**',
            color=0x2b2d31,
            timestamp=discord.utils.utcnow()
        )
        
        
        # Каналы
        welcome_ch = self.config.get('welcome_channel_id')
        app_ch = self.config.get('application_channel_id')
        review_ch = self.config.get('review_channel_id')
        logs_ch = self.config.get('logs_channel_id')
        contracts_ch = self.config.get('contracts_channel_id')
        contracts_members_ch = self.config.get('contracts_members_channel_id')
        
        channels_text = (
            f"**Приветствие:** {f'<#{welcome_ch}>' if welcome_ch else '`Не настроен`'}\n"
            f"**Заявки:** {f'<#{app_ch}>' if app_ch else '`Не настроен`'}\n"
            f"**Рассмотрение:** {f'<#{review_ch}>' if review_ch else '`Не настроен`'}\n"
            f"**Логи:** {f'<#{logs_ch}>' if logs_ch else '`Не настроен`'}\n"
            f"**Контракты (запросы):** {f'<#{contracts_ch}>' if contracts_ch else '`Не настроен`'}\n"
            f"**Контракты (Members):** {f'<#{contracts_members_ch}>' if contracts_members_ch else '`Не настроен`'}"
        )
        
        embed1.add_field(
            name="📺 Каналы",
            value=channels_text,
            inline=False
        )
        
        # Роли
        def get_role_mention(role_id):
            if role_id:
                role = ctx.guild.get_role(role_id)
                return role.mention if role else f"`ID: {role_id}`"
            return "`Не настроена`"
        
        def get_roles_mention(role_ids):
            if not role_ids:
                return "`Не настроены`"
            mentions = []
            for role_id in role_ids:
                role = ctx.guild.get_role(role_id)
                if role:
                    mentions.append(role.mention)
                else:
                    mentions.append(f"`ID: {role_id}`")
            return ", ".join(mentions) if mentions else "`Не настроены`"
        
        owner_roles = self.config.get('owner_role_ids', [])
        dep_owner_roles = self.config.get('dep_owner_role_ids', [])
        dev_roles = self.config.get('dev_role_ids', [])
        contract_role = self.config.get('contract_role_id')
        mod_roles = self.config.get('moderator_role_ids', [])
        family_role = self.config.get('family_role_id')
        member_role = self.config.get('member_role_id')
        auto_role = self.config.get('auto_role_id')
        
        roles_text = (
            f"**Owner:** {get_roles_mention(owner_roles)}\n"
            f"**Dep.Owner:** {get_roles_mention(dep_owner_roles)}\n"
            f"**Developer:** {get_roles_mention(dev_roles)}\n"
            f"**Contract:** {get_role_mention(contract_role)}\n"
            f"**REC:** {get_roles_mention(mod_roles)}\n"
            f"**Family:** {get_role_mention(family_role)}\n"
            f"**Academy:** {get_role_mention(member_role)}\n"
            f"**Guest:** {get_role_mention(auto_role)}"
        )
        
        embed1.add_field(
            name="🎭 Роли",
            value=roles_text,
            inline=False
        )
        
        # Другие настройки
        embed1.add_field(
            name="🔧 Прочее",
            value=f"**Префикс:** `{self.config.get('prefix', '!')}`\n",
            inline=False
        )
        
        embed1.set_footer(text=f"Запросил: {ctx.author.name}")
        
        # Второй embed - Таблица прав (КОМПАКТНАЯ!)
        embed2 = discord.Embed(
            title='🔐 Права доступа',
            color=0x2b2d31
        )
        
        # Администрация
        admin_table = (
            "```\n"
            "Owner     → ВСЕ команды + настройка\n"
            "Dep.Owner → Контракты + Заявки\n"
            "Developer → ВСЕ команды + настройка\n"
            "```"
        )
        
        # Модераторы
        mod_table = (
            "```\n"
            "Contract → Контракты (все действия)\n"
            "REC      → Заявки (одобрение/отклон)\n"
            "```"
        )
        
        # Участники
        member_table = (
            "```\n"
            "Academy/Family → Запрос + Запись\n"
            "```"
        )
        
        embed2.add_field(name="👑 Администрация", value=admin_table, inline=False)
        embed2.add_field(name="👥 Модераторы", value=mod_table, inline=False)
        embed2.add_field(name="🎮 Участники", value=member_table, inline=False)
        
        # Третий embed - Команды
        embed3 = discord.Embed(
            title='📝 Команды настройки',
            color=0x2b2d31
        )
        
        embed3.add_field(
            name="Каналы",
            value=(
                "`!config welcome_channel #канал`\n"
                "`!config application_channel #канал`\n"
                "`!config contracts_channel #канал`"
            ),
            inline=False
        )
        
        embed3.add_field(
            name="Роли",
            value=(
                "`!config owner_role @роль`\n"
                "`!config dev_role @роль`\n"
                "`!config contract_role @роль`"
            ),
            inline=False
        )
        
        # Отправляем все три embed
        await ctx.send(embeds=[embed1, embed2, embed3])
    
    async def update_setting(self, ctx, setting: str, value: str):
        """Обновить настройку"""
        
        if not value:
            await ctx.send(f"❌ Укажите значение для настройки `{setting}`")
            return
        
        # ============ НАСТРОЙКА РОЛЕЙ ============
        
        if setting in ['owner_role', 'owner']:
            role_id = self.parse_role(value, ctx)
            if role_id:
                current_roles = self.config.get('owner_role_ids', [])
                if role_id not in current_roles:
                    current_roles.append(role_id)
                    self.config.set('owner_role_ids', current_roles)
                    await ctx.send(f"✅ Роль Owner добавлена: <@&{role_id}>")
                else:
                    await ctx.send(f"⚠️ Эта роль уже добавлена как Owner")
            else:
                await ctx.send(f"❌ Роль не найдена!")
        
        elif setting in ['dep_owner_role', 'dep_owner', 'depowner']:
            role_id = self.parse_role(value, ctx)
            if role_id:
                current_roles = self.config.get('dep_owner_role_ids', [])
                if role_id not in current_roles:
                    current_roles.append(role_id)
                    self.config.set('dep_owner_role_ids', current_roles)
                    await ctx.send(f"✅ Роль Dep.Owner добавлена: <@&{role_id}>")
                else:
                    await ctx.send(f"⚠️ Эта роль уже добавлена как Dep.Owner")
            else:
                await ctx.send(f"❌ Роль не найдена!")
        
        elif setting in ['dev_role', 'developer', 'dev']:
            role_id = self.parse_role(value, ctx)
            if role_id:
                current_roles = self.config.get('dev_role_ids', [])
                if role_id not in current_roles:
                    current_roles.append(role_id)
                    self.config.set('dev_role_ids', current_roles)
                    await ctx.send(f"✅ Роль Developer добавлена: <@&{role_id}>")
                else:
                    await ctx.send(f"⚠️ Эта роль уже добавлена как Developer")
            else:
                await ctx.send(f"❌ Роль не найдена!")
        
        elif setting in ['contract_role', 'contract']:
            role_id = self.parse_role(value, ctx)
            if role_id:
                self.config.set('contract_role_id', role_id)
                await ctx.send(f"✅ Роль Contract установлена: <@&{role_id}>")
            else:
                await ctx.send(f"❌ Роль не найдена!")
        
        elif setting in ['moderator_role', 'mod_role', 'rec', 'rec_role']:
            role_id = self.parse_role(value, ctx)
            if role_id:
                current_roles = self.config.get('moderator_role_ids', [])
                if role_id not in current_roles:
                    current_roles.append(role_id)
                    self.config.set('moderator_role_ids', current_roles)
                    await ctx.send(f"✅ Роль REC добавлена: <@&{role_id}>")
                else:
                    await ctx.send(f"⚠️ Эта роль уже добавлена как REC")
            else:
                await ctx.send(f"❌ Роль не найдена!")
        
        elif setting in ['family_role', 'family']:
            role_id = self.parse_role(value, ctx)
            if role_id:
                self.config.set('family_role_id', role_id)
                await ctx.send(f"✅ Роль Family установлена: <@&{role_id}>")
            else:
                await ctx.send(f"❌ Роль не найдена!")
        
        elif setting in ['member_role', 'academy', 'price_academy']:
            role_id = self.parse_role(value, ctx)
            if role_id:
                self.config.set('member_role_id', role_id)
                await ctx.send(f"✅ Роль Price Academy установлена: <@&{role_id}>")
            else:
                await ctx.send(f"❌ Роль не найдена!")
        
        elif setting in ['auto_role', 'guest']:
            role_id = self.parse_role(value, ctx)
            if role_id:
                self.config.set('auto_role_id', role_id)
                await ctx.send(f"✅ Авто-роль Guest установлена: <@&{role_id}>")
            else:
                await ctx.send(f"❌ Роль не найдена!")
        
        # ============ НАСТРОЙКА КАНАЛОВ ============
        
        elif setting in ['welcome_channel', 'приветствие']:
            channel_id = self.parse_channel(value, ctx)
            if channel_id:
                self.config.set('welcome_channel_id', channel_id)
                await ctx.send(f"✅ Канал приветствия установлен: <#{channel_id}>")
            else:
                await ctx.send(f"❌ Канал не найден!")
        
        elif setting in ['application_channel', 'заявки']:
            channel_id = self.parse_channel(value, ctx)
            if channel_id:
                self.config.set('application_channel_id', channel_id)
                await ctx.send(f"✅ Канал заявок установлен: <#{channel_id}>")
            else:
                await ctx.send(f"❌ Канал не найден!")
        
        elif setting in ['review_channel', 'рассмотрение']:
            channel_id = self.parse_channel(value, ctx)
            if channel_id:
                self.config.set('review_channel_id', channel_id)
                await ctx.send(f"✅ Канал рассмотрения установлен: <#{channel_id}>")
            else:
                await ctx.send(f"❌ Канал не найден!")
        
        elif setting in ['logs_channel', 'логи']:
            channel_id = self.parse_channel(value, ctx)
            if channel_id:
                self.config.set('logs_channel_id', channel_id)
                await ctx.send(f"✅ Канал логов установлен: <#{channel_id}>")
            else:
                await ctx.send(f"❌ Канал не найден!")
        
        elif setting in ['contracts_channel', 'контракты']:
            channel_id = self.parse_channel(value, ctx)
            if channel_id:
                self.config.set('contracts_channel_id', channel_id)
                await ctx.send(f"✅ Канал контрактов (запросы) установлен: <#{channel_id}>")
            else:
                await ctx.send(f"❌ Канал не найден!")
        
        elif setting in ['contracts_members_channel', 'контракты_members']:
            channel_id = self.parse_channel(value, ctx)
            if channel_id:
                self.config.set('contracts_members_channel_id', channel_id)
                await ctx.send(f"✅ Канал контрактов (Members) установлен: <#{channel_id}>")
            else:
                await ctx.send(f"❌ Канал не найден!")
        
        # ============ ДРУГИЕ НАСТРОЙКИ ============
        
        elif setting == 'logo':
            if value.startswith('http'):
                await ctx.send(f"✅ Логотип обновлен!")
            else:
                await ctx.send(f"❌ Укажите корректный URL (должен начинаться с http)")
        
        else:
            await ctx.send(f"❌ Неизвестная настройка: `{setting}`\n\n"
                          f"Доступные настройки:\n"
                          f"**Роли:** owner_role, dep_owner_role, dev_role, contract_role, moderator_role, family_role, member_role, auto_role\n"
                          f"**Каналы:** welcome_channel, application_channel, review_channel, logs_channel, contracts_channel, contracts_members_channel\n"
                          f"**Прочее:** logo")
    
    def parse_channel(self, value: str, ctx):
        """Парсинг канала из упоминания или ID"""
        # Убираем <# и >
        value = value.strip('<#>')
        
        try:
            channel_id = int(value)
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                return channel_id
            else:
                return None
        except ValueError:
            return None


async def setup(bot):
    """Функция загрузки cog"""
    await bot.add_cog(ConfigCommands(bot))