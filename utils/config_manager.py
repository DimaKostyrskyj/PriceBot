# -*- coding: utf-8 -*-
import json
import os
from typing import Any, Optional

class ConfigManager:
    """Configuration manager for the bot"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            print(f"Config file {self.config_file} not found, creating new one...")
            return self._create_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error reading {self.config_file}: {e}, creating new one...")
            return self._create_default_config()
    
    def _create_default_config(self) -> dict:
        """Create default configuration"""
        default_config = {
            "prefix": "!",
            "welcome_channel_id": 0,
            "application_channel_id": 0,
            "review_channel_id": 0,
            "logs_channel_id": 0,
            "moderator_role_ids": [],
            "member_role_id": 0,
            "auto_role_id": 0,
            "dev_role_ids": [],
            "owner_role_ids": [],
            "logo_url": "https://cdn.discordapp.com/attachments/1255612946952753286/1443000704552665272/Black_White_Minimal_Modern_Simple_Bold_Business_Mag_Logo_3.png?ex=69277aa1&is=69262921&hm=4bd700d3db86c8ff9fe8e06b838ce927220c6d584d0307bbf559e6224a477004&",
            "colors": {
                "primary": "0xFFD700",
                "success": "0x00FF00",
                "error": "0xFF0000",
                "warning": "0xFFA500",
                "info": "0x00BFFF"
            }
        }
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Optional[dict] = None) -> None:
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Ошибка сохранения конфигурации: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from configuration"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set value in configuration"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def get_color(self, color_name: str) -> int:
        """Get color from configuration"""
        color = self.get(f'colors.{color_name}', '0xFFD700')
        if isinstance(color, str):
            # Убираем префикс 0x если есть
            color_clean = color.replace('0x', '').replace('#', '')
            return int(color_clean, 16)
        return color
    
    def reload(self) -> None:
        """Reload configuration"""
        self.config = self.load_config()