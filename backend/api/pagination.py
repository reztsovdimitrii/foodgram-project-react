""""
Создание пагинатора.
"""

from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Создание пагинатора, наследуемого от PageNumberPagination.
    """
    page_size = 6
    page_size_query_param = 'limit'