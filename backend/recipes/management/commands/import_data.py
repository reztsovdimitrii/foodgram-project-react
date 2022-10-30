import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'импорт фикстур из директории: data'

    def handle(self, *args, **options):
        # import Ingredient model
        path = './data/ingredients.csv'
        with open(path, 'r', newline='', encoding='utf-8') as data:
            result = csv.DictReader(data, delimiter=',')
            for line in result:
                try:
                    name = line['name']
                    measurement_unit = line['measurement_unit']
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
                except Exception as error_ingredient:
                    print(
                        f'упали на разборе строки продукта {name}:'
                        f' {error_ingredient}'
                    )
        # import Tag model
        path = './data/tags.csv'
        with open(path, 'r', newline='', encoding='utf-8') as data:
            result = csv.DictReader(data, delimiter=',')
            for line in result:
                try:
                    name = line['name']
                    color = line['color']
                    slug = line['slug']
                    Tag.objects.get_or_create(
                        name=name,
                        color=color,
                        slug=slug,
                    )
                except Exception as error_tag:
                    print(f'упали на разборе строки тега {name}: {error_tag}')
