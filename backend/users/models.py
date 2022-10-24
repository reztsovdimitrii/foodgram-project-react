"""
Создание модели пользователя.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Создание своей модели пользователя.
    """
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = {
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    }
    username = models.CharField(
        db_index=True,
        max_length=150,
        unique=True,
        null=False,
        blank=False,
        verbose_name='Логин',
        help_text='Введите уникальный логин'
    )
    email = models.EmailField(
        db_index=True,
        null=False,
        blank=False,
        unique=True,
        max_length=254,
        verbose_name='Электронная почта',
        help_text='Введите электронную почту'
    )
    first_name = models.CharField(
        max_length=254,
        null=False,
        blank=False,
        verbose_name='Имя',
        help_text='Введите имя пользователя'
    )
    last_name = models.CharField(
        max_length=254,
        null=False,
        blank=False,
        verbose_name='Фамилия',
        help_text='Введите фамилию пользователя'
    )
    role = models.CharField(
        verbose_name='статус',
        max_length=20,
        choices=ROLES,
        default=USER,
    )
    date_joined = models.DateTimeField(
        verbose_name='Дата регистрации',
        auto_now_add=True,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
        help_text='Введите пароль',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=['username', 'email'],
                                    name='uniq_signup'),
        )

    def __str__(self) -> str:
        """Строковое представление модели (отображается в консоли)."""
        return self.username
