# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from utils.config_manager import ConfigManager

# Загрузка переменных окружения
load_dotenv()

# Загрузка конфигурации
config = ConfigManager()

# Настройка intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

class PriceFamQBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config.get('prefix', '!'),
            intents=intents,
            help_command=None
        )
        
    async def setup_hook(self):
        """Загрузка всех cogs при запуске"""
        print("🔄 Загрузка модулей...")
        
        # Загрузка всех cogs из папки cogs
        cogs_to_load = [
            'cogs.diagnostics',  # Диагностика - первым!
            'cogs.welcome',
            'cogs.applications',
            'cogs.logs',
            'cogs.config_commands',
            'cogs.contracts',
            'cogs.help'
        ]
        
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                print(f"✅ Модуль {cog} загружен")
            except Exception as e:
                print(f"❌ Ошибка загрузки модуля {cog}: {e}")
        
        print("✅ Все модули загружены")
        
    async def on_ready(self):
        """Событие готовности бота"""
        print("\n" + "="*50)
        print(f"✅ Бот {self.user.name} успешно запущен!")
        print(f"🆔 ID: {self.user.id}")
        print(f"🔗 Подключен к {len(self.guilds)} серверам")
        print(f"👥 Доступно пользователей: {len(self.users)}")
        print("="*50 + "\n")
        
        # Установка статуса
        activity = discord.Game(name="🏠 Price FamQ | !help")
        await self.change_presence(status=discord.Status.online, activity=activity)
    
    async def on_message(self, message):
        """КРИТИЧНО: Обработка команд!"""
        # Игнорируем сообщения от ботов
        if message.author.bot:
            return
        
        # ВАЖНО: Обрабатываем команды
        await self.process_commands(message)

def main():
    """Главная функция запуска бота"""
    # Проверка токена
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        print("❌ ОШИБКА: Токен бота не найден!")
        print("📝 Создайте файл .env и добавьте:")
        print("   DISCORD_BOT_TOKEN=ваш_токен_здесь")
        return
    
    # Создание и запуск бота
    bot = PriceFamQBot()
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("❌ ОШИБКА: Неверный токен бота!")
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")

if __name__ == "__main__":
    main()