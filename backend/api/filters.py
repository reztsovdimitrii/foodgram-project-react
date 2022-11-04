"""
Настройка пользовательских фильтров.
"""

from django_filters import rest_framework as django_filter
from recipes.models import Recipe
from rest_framework import filters
from users.models import User


class RecipeFilters(django_filter.FilterSet):
    """
    Настройка фильтров модели рецептов.
    """
    author = django_filter.ModelChoiceFilter(queryset=User.objects.all())
    tags = django_filter.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = django_filter.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = django_filter.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        """
        Мета параметры фильтров модели рецептов.
        """
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        """
        Метод обработки фильтров параметра is_favorited.
        """
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """
        Метод обработки фильтров параметра is_in_shopping_cart.
        """
        if self.request.user.is_authenticated and value:
            return queryset.filter(carts__user=self.request.user)
        return queryset.all()


class IngredientSearchFilter(filters.SearchFilter):
    """
    Настройка фильтра поиска модели продуктов.
    """
    search_param = 'name'
