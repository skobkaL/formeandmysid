from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.TextChoices):
    STOREKEEPER = 'storekeeper', 'Кладовщик'
    FOREMAN = 'foreman', 'Прораб'
    SUPPLY_MANAGER = 'supply_manager', 'Менеджер снабжения'
    CHIEF_ENGINEER = 'chief_engineer', 'Главный инженер'
    ACCOUNTANT = 'accountant', 'Бухгалтер'
    ADMIN = 'admin', 'Администратор'

class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STOREKEEPER)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    @property
    def can_manage_tools(self):
        return self.role in [Role.STOREKEEPER, Role.SUPPLY_MANAGER, Role.CHIEF_ENGINEER, Role.ADMIN]
    
    @property
    def can_issue_return(self):
        return self.role in [Role.STOREKEEPER, Role.FOREMAN, Role.ADMIN]
    
    @property
    def can_view_reports(self):
        return self.role in [Role.SUPPLY_MANAGER, Role.CHIEF_ENGINEER, Role.ACCOUNTANT, Role.ADMIN]