from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from menus.factories import DishFactory, MenuFactory
from menus.serializers import DishSerializer, MenuSerializer
from rest_framework.exceptions import ErrorDetail


class MenuSerializerTest(TestCase):
    def test_unique_menu_name(self):
        MenuFactory(name='Test menu')
        data = {'name': 'Test menu', 'description': 'Test description'}
        serializer = MenuSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors, {'name': [ErrorDetail(string='menu with this name already exists.', code='unique')]}
        )

    @freeze_time("2021-10-3")
    def test_create_menu(self):
        data = {'name': 'Test menu', 'description': 'Test description'}
        serializer = MenuSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        menu = serializer.save()

        self.assertEqual(menu.name, data['name'])
        self.assertEqual(menu.description, data['description'])
        self.assertEqual(menu.created, timezone.now())
        self.assertEqual(menu.updated, None)

    @freeze_time("2021-10-3")
    def test_update_menu(self):
        menu = MenuFactory(name='Test menu')
        data = {'name': 'Test menu', 'description': 'Updated description'}
        serializer = MenuSerializer(menu, data=data)
        serializer.is_valid(raise_exception=True)
        menu = serializer.save()

        self.assertEqual(menu.name, data['name'])
        self.assertEqual(menu.description, data['description'])
        self.assertEqual(menu.updated, timezone.now())


class DishSerializerTest(TestCase):
    def setUp(self):
        self.menu = MenuFactory()
        self.context = dict(menu=self.menu)

    @freeze_time("2021-10-3")
    def test_create_dish(self):
        data = {
            'name': 'Test dish',
            'description': 'Test dish description',
            'price': '24.99',
            'time_to_prepare': 30,
            'is_vegetarian': False,
        }
        serializer = DishSerializer(data=data, context=self.context)
        serializer.is_valid(raise_exception=True)
        dish = serializer.save()

        self.assertEqual(dish.menu, self.menu)
        self.assertEqual(dish.name, data['name'])
        self.assertEqual(dish.description, data['description'])
        self.assertEqual(dish.price, Decimal(data['price']))
        self.assertEqual(dish.time_to_prepare, data['time_to_prepare'])
        self.assertEqual(dish.is_vegetarian, data['is_vegetarian'])
        self.assertEqual(dish.created, timezone.now())
        self.assertEqual(dish.updated, None)

        self.menu.refresh_from_db()
        self.assertEqual(self.menu.updated, timezone.now())

    @freeze_time("2021-10-3")
    def test_update_dish(self):
        dish = DishFactory(menu=self.menu)
        data = {
            'name': 'Test dish',
            'description': 'Test dish description',
            'price': '24.99',
            'time_to_prepare': 30,
            'is_vegetarian': False,
        }
        serializer = DishSerializer(dish, data=data, context=self.context)
        serializer.is_valid(raise_exception=True)
        dish = serializer.save()

        self.assertEqual(dish.menu, self.menu)
        self.assertEqual(dish.name, data['name'])
        self.assertEqual(dish.description, data['description'])
        self.assertEqual(dish.price, Decimal(data['price']))
        self.assertEqual(dish.time_to_prepare, data['time_to_prepare'])
        self.assertEqual(dish.is_vegetarian, data['is_vegetarian'])
        self.assertEqual(dish.created, timezone.now())
        self.assertEqual(dish.updated, timezone.now())

        self.menu.refresh_from_db()
        self.assertEqual(self.menu.updated, timezone.now())
