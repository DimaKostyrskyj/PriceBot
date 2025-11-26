import discord
from discord.ext import commands
from datetime import datetime
import json
import os
from utils.config_manager import ConfigManager

class Logs(commands.Cog):
    """Модуль логирования и скачивания логов"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()
        self.logs_dir = "logs"
        self.logs_file = os.path.join(self.logs_dir, "bot_logs.json")
        
        # Создаем папку для логов если её нет
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        
        # Создаем файл логов если его нет
        if not os.path.exists(self.logs_file):
            with open(self.logs_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def _check_log_permissions(self, interaction_or_ctx) -> bool:
        """Проверка прав на просмотр/скачивание логов"""
        dev_role_ids = self.config.get('dev_role_ids', [])
        owner_role_ids = self.config.get('owner_role_ids', [])
        allowed_roles = dev_role_ids + owner_role_ids
        
        if hasattr(interaction_or_ctx, 'user'):
            # Это interaction
            user = interaction_or_ctx.user
        else:
            # Это context
            user = interaction_or_ctx.author
        
        return any(role.id in allowed_roles for role in user.roles)
    
    def add_log(self, log_type: str, data: dict):
        """Добавление записи в лог"""
        try:
            # Читаем существующие логи
            with open(self.logs_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # Добавляем новую запись
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': log_type,
                'data': data
            }
            logs.append(log_entry)
            
            # Ограничиваем количество логов (последние 1000)
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # Сохраняем логи
            with open(self.logs_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"❌ Ошибка при добавлении лога: {e}")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Логирование удаленных сообщений"""
        if message.author.bot:
            return
        
        self.add_log('message_delete', {
            'user_id': message.author.id,
            'user_name': message.author.name,
            'channel_id': message.channel.id,
            'channel_name': message.channel.name,
            'content': message.content[:500]  # Ограничиваем длину
        })
        
        # Отправляем в канал логов
        await self._send_log_embed(
            title='🗑️ Сообщение удалено',
            description=f'**Автор:** {message.author.mention}\n**Канал:** {message.channel.mention}',
            fields=[
                {'name': 'Содержание', 'value': message.content[:1000] if message.content else '*Пусто*', 'inline': False}
            ],
            color=self.config.get_color('warning')
        )
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Логирование отредактированных сообщений"""
        if before.author.bot or before.content == after.content:
            return
        
        self.add_log('message_edit', {
            'user_id': before.author.id,
            'user_name': before.author.name,
            'channel_id': before.channel.id,
            'channel_name': before.channel.name,
            'before': before.content[:500],
            'after': after.content[:500]
        })
        
        # Отправляем в канал логов
        await self._send_log_embed(
            title='✏️ Сообщение отредактировано',
            description=f'**Автор:** {before.author.mention}\n**Канал:** {before.channel.mention}',
            fields=[
                {'name': 'До', 'value': before.content[:500] if before.content else '*Пусто*', 'inline': False},
                {'name': 'После', 'value': after.content[:500] if after.content else '*Пусто*', 'inline': False}
            ],
            color=self.config.get_color('info')
        )
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        """Логирование банов"""
        self.add_log('member_ban', {
            'user_id': user.id,
            'user_name': user.name,
            'guild_id': guild.id,
            'guild_name': guild.name
        })
        
        await self._send_log_embed(
            title='🔨 Пользователь забанен',
            description=f'**Пользователь:** {user.mention} ({user.name})',
            fields=[
                {'name': 'ID', 'value': str(user.id), 'inline': True}
            ],
            color=self.config.get_color('error')
        )
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        """Логирование разбанов"""
        self.add_log('member_unban', {
            'user_id': user.id,
            'user_name': user.name,
            'guild_id': guild.id,
            'guild_name': guild.name
        })
        
        await self._send_log_embed(
            title='✅ Пользователь разбанен',
            description=f'**Пользователь:** {user.mention} ({user.name})',
            fields=[
                {'name': 'ID', 'value': str(user.id), 'inline': True}
            ],
            color=self.config.get_color('success')
        )
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        """Логирование создания каналов"""
        self.add_log('channel_create', {
            'channel_id': channel.id,
            'channel_name': channel.name,
            'channel_type': str(channel.type)
        })
        
        await self._send_log_embed(
            title='➕ Канал создан',
            description=f'**Канал:** {channel.mention}',
            fields=[
                {'name': 'Тип', 'value': str(channel.type), 'inline': True},
                {'name': 'ID', 'value': str(channel.id), 'inline': True}
            ],
            color=self.config.get_color('success')
        )
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        """Логирование удаления каналов"""
        self.add_log('channel_delete', {
            'channel_id': channel.id,
            'channel_name': channel.name,
            'channel_type': str(channel.type)
        })
        
        await self._send_log_embed(
            title='➖ Канал удален',
            description=f'**Канал:** {channel.name}',
            fields=[
                {'name': 'Тип', 'value': str(channel.type), 'inline': True},
                {'name': 'ID', 'value': str(channel.id), 'inline': True}
            ],
            color=self.config.get_color('error')
        )
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        """Логирование создания ролей"""
        self.add_log('role_create', {
            'role_id': role.id,
            'role_name': role.name
        })
        
        await self._send_log_embed(
            title='🎭 Роль создана',
            description=f'**Роль:** {role.mention}',
            fields=[
                {'name': 'ID', 'value': str(role.id), 'inline': True}
            ],
            color=self.config.get_color('success')
        )
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        """Логирование удаления ролей"""
        self.add_log('role_delete', {
            'role_id': role.id,
            'role_name': role.name
        })
        
        await self._send_log_embed(
            title='🎭 Роль удалена',
            description=f'**Роль:** {role.name}',
            fields=[
                {'name': 'ID', 'value': str(role.id), 'inline': True}
            ],
            color=self.config.get_color('error')
        )
    
    async def _send_log_embed(self, title: str, description: str, fields: list, color: int):
        """Отправка embed в канал логов"""
        logs_channel_id = self.config.get('logs_channel_id')
        if not logs_channel_id:
            return
        
        logs_channel = self.bot.get_channel(logs_channel_id)
        if not logs_channel:
            return
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now()
        )
        
        for field in fields:
            embed.add_field(
                name=field['name'],
                value=field['value'],
                inline=field.get('inline', False)
            )
        
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass
        except Exception as e:
            print(f"❌ Ошибка при отправке лога: {e}")
    
    @commands.command(name='download_logs')
    async def download_logs(self, ctx, days: int = 7):
        """
        Скачать логи (только для Dev и Owner)
        Использование: !download_logs [количество_дней]
        """
        if not self._check_log_permissions(ctx):
            await ctx.send('❌ У вас нет прав для скачивания логов! Требуется роль Dev или Owner.')
            return
        
        try:
            # Читаем логи
            with open(self.logs_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            if not logs:
                await ctx.send('📭 Логи пустые.')
                return
            
            # Фильтруем логи по дням
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            filtered_logs = [
                log for log in logs
                if datetime.fromisoformat(log['timestamp']) > cutoff_date
            ]
            
            if not filtered_logs:
                await ctx.send(f'📭 Нет логов за последние {days} дней.')
                return
            
            # Создаем временный файл с логами
            temp_file = f"logs_last_{days}_days.json"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_logs, f, indent=2, ensure_ascii=False)
            
            # Создаем embed
            embed = discord.Embed(
                title='📥 Скачивание логов',
                description=f'Логи за последние {days} дней',
                color=self.config.get_color('info'),
                timestamp=datetime.now()
            )
            embed.add_field(name='Записей', value=str(len(filtered_logs)), inline=True)
            embed.add_field(name='Запросил', value=ctx.author.mention, inline=True)
            embed.set_footer(text='Price FamQ • Логи')
            
            # Отправляем файл
            await ctx.send(embed=embed, file=discord.File(temp_file))
            
            # Удаляем временный файл
            os.remove(temp_file)
            
            # Логируем скачивание
            self.add_log('logs_download', {
                'user_id': ctx.author.id,
                'user_name': ctx.author.name,
                'days': days,
                'records_count': len(filtered_logs)
            })
            
            # Уведомляем в канал логов
            await self._send_log_embed(
                title='📥 Логи скачаны',
                description=f'{ctx.author.mention} скачал логи',
                fields=[
                    {'name': 'Период', 'value': f'{days} дней', 'inline': True},
                    {'name': 'Записей', 'value': str(len(filtered_logs)), 'inline': True}
                ],
                color=self.config.get_color('warning')
            )
        
        except Exception as e:
            await ctx.send(f'❌ Ошибка при скачивании логов: {e}')
            print(f"❌ Ошибка download_logs: {e}")
    
    @commands.command(name='clear_logs')
    async def clear_logs(self, ctx):
        """Очистить все логи (только для Owner)"""
        owner_role_ids = self.config.get('owner_role_ids', [])
        
        if not any(role.id in owner_role_ids for role in ctx.author.roles):
            await ctx.send('❌ У вас нет прав для очистки логов! Требуется роль Owner.')
            return
        
        try:
            # Создаем резервную копию перед очисткой
            backup_file = f"logs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(self.logs_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            with open(os.path.join(self.logs_dir, backup_file), 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            
            # Очищаем логи
            with open(self.logs_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            
            embed = discord.Embed(
                title='🗑️ Логи очищены',
                description=f'Все логи были очищены пользователем {ctx.author.mention}',
                color=self.config.get_color('warning'),
                timestamp=datetime.now()
            )
            embed.add_field(name='Удалено записей', value=str(len(logs)), inline=True)
            embed.add_field(name='Резервная копия', value=backup_file, inline=True)
            
            await ctx.send(embed=embed)
            
            # Логируем очистку
            await self._send_log_embed(
                title='🗑️ Логи очищены',
                description=f'{ctx.author.mention} очистил все логи',
                fields=[
                    {'name': 'Удалено записей', 'value': str(len(logs)), 'inline': True},
                    {'name': 'Резервная копия', 'value': backup_file, 'inline': True}
                ],
                color=self.config.get_color('error')
            )
        
        except Exception as e:
            await ctx.send(f'❌ Ошибка при очистке логов: {e}')
            print(f"❌ Ошибка clear_logs: {e}")
    
    @commands.command(name='logs_stats')
    async def logs_stats(self, ctx):
        """Статистика логов (для Dev и Owner)"""
        if not self._check_log_permissions(ctx):
            await ctx.send('❌ У вас нет прав для просмотра статистики логов!')
            return
        
        try:
            with open(self.logs_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # Подсчет статистики
            stats = {}
            for log in logs:
                log_type = log.get('type', 'unknown')
                stats[log_type] = stats.get(log_type, 0) + 1
            
            embed = discord.Embed(
                title='📊 Статистика логов',
                color=self.config.get_color('info'),
                timestamp=datetime.now()
            )
            
            embed.add_field(name='Всего записей', value=str(len(logs)), inline=False)
            
            # Добавляем статистику по типам
            if stats:
                stats_text = '\n'.join([f'`{k}`: {v}' for k, v in sorted(stats.items(), key=lambda x: x[1], reverse=True)])
                embed.add_field(name='По типам', value=stats_text, inline=False)
            
            # Размер файла
            file_size = os.path.getsize(self.logs_file) / 1024  # KB
            embed.add_field(name='Размер файла', value=f'{file_size:.2f} KB', inline=True)
            
            await ctx.send(embed=embed)
        
        except Exception as e:
            await ctx.send(f'❌ Ошибка при получении статистики: {e}')


async def setup(bot):
    """Функция загрузки cog"""
    await bot.add_cog(Logs(bot))