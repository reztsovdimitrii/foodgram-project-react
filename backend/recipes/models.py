from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

from .fields import HexColorField


class Tag(models.Model):
    """
    Модель тегов.
    name - название тега
    color - HEX-код цвета
    slug - идентификатор в URL.
    """
    name = models.CharField(
        verbose_name='Название',
        max_length=40,
        unique=True,
        null=False,
        help_text='Название тега',
    )
    color = HexColorField(
        verbose_name='HEX-код цвета',
        unique=True,
        null=True,
        help_text='Выберите цвет',
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        unique=True,
        help_text='Придумайте уникальный URL адрес для тега',
    )

    class Meta:
        ordering = '-id',
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Создание модели продуктов.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название продукта',
        help_text='Введите название продуктов'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
        help_text='Введите единицы измерения'
    )

    class Meta:
        """
        Мета параметры модели.
        """
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        """"
        Метод строкового представления модели.
        """
        return self.name


class Recipe(models.Model):
    """
    Создание модели рецептов.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Выберите автора рецепта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите описание рецепта'
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления',
        help_text='Введите время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        help_text='Добавить дату создания'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Теги рецепта',
        help_text='Выберите теги рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Продукты в рецепте',
        help_text='Выберите продукты рецепта')

    class Meta:
        """
        Мета параметры модели.
        """
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """"
        Метод строкового представления модели.
        """
        return self.name


class Cart(models.Model):
    """
    Создание модели корзины.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Рецепты',
        help_text='Выберите рецепты для добавления в корзины'
    )

    class Meta:
        """
        Мета параметры модели.
        """
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_cart')
        ]

    def __str__(self):
        """"
        Метод строкового представления модели.
        """
        return f'{self.user} {self.recipe}'


class Subscribe(models.Model):
    """
    Создание модели подписок.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
        help_text='Выберите пользователя, который подписывается'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Выберите автора, на которого подписываются'
    )

    class Meta:
        """
        Мета параметры модели.
        """
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'following'],
                                    name='unique_subscribe')
        ]

    def __str__(self):
        """"
        Метод строкового представления модели.
        """
        return f'{self.user} {self.following}'


class TagRecipe(models.Model):
    """
    Создание модели тегов рецепта.
    """
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Теги',
        help_text='Выберите теги рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )

    class Meta:
        """
        Мета параметры модели.
        """
        verbose_name = 'Теги рецепта'
        verbose_name_plural = 'Теги рецепта'
        constraints = [
            models.UniqueConstraint(fields=['tag', 'recipe'],
                                    name='unique_tagrecipe')
        ]

    def __str__(self):
        """"
        Метод строкового представления модели.
        """
        return f'{self.tag} {self.recipe}'


class IngredientRecipe(models.Model):
    """
    Создание модели продуктов в рецепте.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredientrecipes',
        verbose_name='Продукты рецепта',
        help_text='Добавить продукты рецепта в корзину')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredientrecipes',
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )
    amount = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество продукта',
        help_text='Введите количество продукта'
    )

    class Meta:
        """
        Мета параметры модели.
        """
        verbose_name = 'Продукты в рецепте'
        verbose_name_plural = 'Продукты в рецепте'
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique_ingredientrecipe')
        ]

    def __str__(self):
        """"
        Метод строкового представления модели.
        """
        return f'{self.ingredient} {self.recipe}'


class Favorite(models.Model):
    """
    Создание модели избранных рецептов.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )

    class Meta:
        """
        Мета параметры модели.
        """
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite')
        ]

    def __str__(self):
        """"
        Метод строкового представления модели.
        """
        return f'{self.recipe} {self.user}'
