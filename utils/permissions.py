# -*- coding: utf-8 -*-
"""
Модуль проверки прав доступа для Price FamQ Bot
"""
from utils.config_manager import ConfigManager

class PermissionChecker:
    """Класс для проверки прав доступа пользователей"""
    
    def __init__(self):
        self.config = ConfigManager()
    
    def get_user_role_ids(self, user):
        """Получить список ID ролей пользователя"""
        return [role.id for role in user.roles]
    
    # ============================================================
    # ВЫСШИЙ УРОВЕНЬ - Owner (полный доступ ко всему)
    # ============================================================
    
    def is_owner(self, user) -> bool:
        """Проверка: является ли пользователь Owner"""
        owner_role_ids = self.config.get('owner_role_ids', [])
        user_role_ids = self.get_user_role_ids(user)
        return any(role_id in user_role_ids for role_id in owner_role_ids)
    
    # ============================================================
    # УРОВЕНЬ АДМИНИСТРАЦИИ
    # ============================================================
    
    def is_dep_owner(self, user) -> bool:
        """Проверка: является ли пользователь Dep.Owner"""
        dep_owner_role_ids = self.config.get('dep_owner_role_ids', [])
        user_role_ids = self.get_user_role_ids(user)
        return any(role_id in user_role_ids for role_id in dep_owner_role_ids)
    
    def is_developer(self, user) -> bool:
        """Проверка: является ли пользователь Developer"""
        dev_role_ids = self.config.get('dev_role_ids', [])
        user_role_ids = self.get_user_role_ids(user)
        return any(role_id in user_role_ids for role_id in dev_role_ids)
    
    def is_contract_manager(self, user) -> bool:
        """Проверка: является ли пользователь Contract"""
        contract_role_id = self.config.get('contract_role_id', 0)
        user_role_ids = self.get_user_role_ids(user)
        return contract_role_id in user_role_ids
    
    def is_moderator(self, user) -> bool:
        """Проверка: является ли пользователь REC (модератор)"""
        moderator_role_ids = self.config.get('moderator_role_ids', [])
        user_role_ids = self.get_user_role_ids(user)
        return any(role_id in user_role_ids for role_id in moderator_role_ids)
    
    # ============================================================
    # КОМПЛЕКСНЫЕ ПРОВЕРКИ ДЛЯ ФУНКЦИЙ
    # ============================================================
    
    def can_use_all_commands(self, user) -> bool:
        """
        Проверка: может ли использовать ВСЕ команды и действия
        Роли: Owner, Developer
        """
        return self.is_owner(user) or self.is_developer(user)
    
    def can_manage_contracts(self, user) -> bool:
        """
        Проверка: может ли управлять контрактами (создавать, запускать, завершать)
        Роли: Owner, Dep.Owner, Developer, Contract
        """
        return (
            self.is_owner(user) or
            self.is_dep_owner(user) or
            self.is_developer(user) or
            self.is_contract_manager(user)
        )
    
    def can_review_applications(self, user) -> bool:
        """
        Проверка: может ли рассматривать заявки (одобрять/отклонять)
        Роли: Owner, Dep.Owner, Developer, REC
        """
        return (
            self.is_owner(user) or
            self.is_dep_owner(user) or
            self.is_developer(user) or
            self.is_moderator(user)
        )
    
    def can_use_config(self, user) -> bool:
        """
        Проверка: может ли использовать команду !config
        Роли: Owner, Developer
        """
        return self.is_owner(user) or self.is_developer(user)
    
    def can_participate_in_contracts(self, user) -> bool:
        """
        Проверка: может ли записываться на контракты и запрашивать их
        Роли: Price Academy, Family, и все остальные
        """
        # Все могут записываться на контракты
        return True
    
    # ============================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ============================================================
    
    def get_highest_role_name(self, user) -> str:
        """Получить название самой высокой роли пользователя"""
        if self.is_owner(user):
            return "Owner"
        elif self.is_dep_owner(user):
            return "Dep.Owner"
        elif self.is_developer(user):
            return "Developer"
        elif self.is_contract_manager(user):
            return "Contract"
        elif self.is_moderator(user):
            return "REC"
        else:
            return "Member"
    
    def get_permission_level(self, user) -> int:
        """
        Получить уровень прав (чем выше, тем больше прав)
        5 - Owner
        4 - Dep.Owner
        3 - Developer
        2 - Contract/REC
        1 - Member
        """
        if self.is_owner(user):
            return 5
        elif self.is_dep_owner(user):
            return 4
        elif self.is_developer(user):
            return 3
        elif self.is_contract_manager(user) or self.is_moderator(user):
            return 2
        else:
            return 1


# Создаем глобальный экземпляр
permissions = PermissionChecker()