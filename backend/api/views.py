from http import HTTPStatus

from django.db.models import Sum
from django.shortcuts import get_list_or_404, get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from djoser.views import UserViewSet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from rest_framework import permissions, viewsets
from rest_framework.response import Response

from recipes.models import (
    Cart, Favorite, Ingredient, IngredientRecipe,
    Recipe, Subscribe, Tag
)
from users.models import User
from .serializers import (IngredientSerializer, TagSerializer,
                          RegistrationSerializer, SubscriptionSerializer,
                          RecipeSerializerPost, RecipeSerializer,
                          CartSerializer, FavoriteSerializer)
from .filters import IngredientSearchFilter, RecipeFilters


class CreateUserView(UserViewSet):
    """
    Вьюсет обработки моделей пользователя.
    """
    serializer_class = RegistrationSerializer

    def get_queryset(self):
        return User.objects.all()


class SubscribeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет обработки моделей подписок.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_list_or_404(User, following__user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Метод создания подписки.
        """
        user_id = self.kwargs.get('users_id')
        user = get_object_or_404(User, id=user_id)
        Subscribe.objects.create(
            user=request.user, following=user)
        return Response(HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        """
        Метод удаления подписок.
        """
        author_id = self.kwargs['users_id']
        user_id = request.user.id
        subscribe = get_object_or_404(
            Subscribe, user__id=user_id, following__id=author_id)
        subscribe.delete()
        return Response(HTTPStatus.NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет обработки моделей тегов.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет обработки моделей ингредиентов.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, IngredientSearchFilter)
    pagination_class = None
    search_fields = ['^name']


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет обработки моделей рецептов.
    """
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_class = RecipeFilters
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        """
        Метод подстановки параметров автора при создании рецепта.
        """
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """
        Метод выбора сериализатора в зависимости от запроса.
        """
        if self.request.method == 'GET':
            return RecipeSerializer
        else:
            return RecipeSerializerPost


class BaseFavoriteCartViewSet(viewsets.ModelViewSet):
    """
    Базовый вьюсет обработки модели корзины и избранных рецептов.
    """
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Метод создания модели корзины или избранных рецептов.
        """
        recipe_id = int(self.kwargs['recipes_id'])
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.model.objects.create(
            user=request.user, recipe=recipe)
        return Response(HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        """
        Метод удаления объектов модели корзины или избранных рецептов.
        """
        recipe_id = self.kwargs['recipes_id']
        user_id = request.user.id
        object = get_object_or_404(
            self.model, user__id=user_id, recipe__id=recipe_id)
        object.delete()
        return Response(HTTPStatus.NO_CONTENT)


class CartViewSet(BaseFavoriteCartViewSet):
    """
    Вьюсет обработки модели корзины.
    """
    serializer_class = CartSerializer
    queryset = Cart.objects.all()
    model = Cart


class FavoriteViewSet(BaseFavoriteCartViewSet):
    """
    Вьюсет обработки модели избранных рецептов.
    """
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()
    model = Favorite


class DownloadCart(viewsets.ModelViewSet):
    """
    Сохранение файла списка покупок.
    """
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def canvas_method(dictionary):
        """
        Метод сохранения списка покупок в формате PDF.
        """
        response = HttpResponse(content_type='application/pdf')
        response[
            'Content-Disposition'] = 'attachment; \
        filename = "shopping_cart.pdf"'
        begin_position_x, begin_position_y = 40, 650
        sheet = canvas.Canvas(response, pagesize=A4)
        pdfmetrics.registerFont(TTFont('FreeSans',
                                       'data/FreeSans.ttf'))
        sheet.setFont('FreeSans', 50)
        sheet.setTitle('Список покупок')
        sheet.drawString(begin_position_x,
                         begin_position_y + 40, 'Список покупок: ')
        sheet.setFont('FreeSans', 24)
        for number, item in enumerate(dictionary, start=1):
            if begin_position_y < 100:
                begin_position_y = 700
                sheet.showPage()
                sheet.setFont('FreeSans', 24)
            sheet.drawString(
                begin_position_x,
                begin_position_y,
                f'{number}.  {item["ingredient__name"]} - '
                f'{item["ingredient_total"]}'
                f' {item["ingredient__measurement_unit"]}'
            )
            begin_position_y -= 30
        sheet.showPage()
        sheet.save()
        return response

    def download(self, request):
        """
        Метод создания списка покупок.
        """
        result = IngredientRecipe.objects.filter(
            recipe__carts__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').order_by(
                'ingredient__name').annotate(ingredient_total=Sum('amount'))
        return self.canvas_method(result)
