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
        data = {'name': 'Test menu', 'description': 'Test description', 'dishes': []}
        serializer = MenuSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors, {'name': [ErrorDetail(string='menu with this name already exists.', code='unique')]}
        )

    @freeze_time("2021-10-3")
    def test_create_menu(self):
        dish = DishFactory()
        data = {'name': 'Test menu', 'description': 'Test description', 'dishes': [dish.pk]}
        serializer = MenuSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        menu = serializer.save()

        self.assertEqual(menu.name, data['name'])
        self.assertEqual(menu.description, data['description'])
        self.assertEqual(list(menu.dishes.all()), [dish])
        self.assertEqual(menu.created, timezone.now())
        self.assertEqual(menu.updated, None)

    @freeze_time("2021-10-3")
    def test_update_menu(self):
        old_dish, new_dish = DishFactory.create_batch(2)
        menu = MenuFactory(name='Test menu', dishes=(old_dish,))
        data = {'name': 'Test menu', 'description': 'Updated description', 'dishes': [new_dish.pk]}
        serializer = MenuSerializer(menu, data=data)
        serializer.is_valid(raise_exception=True)
        menu = serializer.save()

        self.assertEqual(menu.name, data['name'])
        self.assertEqual(menu.description, data['description'])
        self.assertEqual(list(menu.dishes.all()), [new_dish])
        self.assertEqual(menu.updated, timezone.now())


class DishSerializerTest(TestCase):
    def setUp(self):
        self.data = {
            'name': 'Test dish',
            'description': 'Test dish description',
            'price': '24.99',
            'time_to_prepare': 30,
            'is_vegetarian': False,
        }

    @freeze_time("2021-10-3")
    def test_reject_negative_price(self):
        data = {**self.data, 'price': '-14'}
        serializer = DishSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, {'price': [ErrorDetail(string='Price must be positive.', code='invalid')]})

    @freeze_time("2021-10-3")
    def test_create_dish(self):
        serializer = DishSerializer(data=self.data)
        serializer.is_valid(raise_exception=True)
        dish = serializer.save()

        self.assertEqual(dish.name, self.data['name'])
        self.assertEqual(dish.description, self.data['description'])
        self.assertEqual(dish.price, Decimal(self.data['price']))
        self.assertEqual(dish.time_to_prepare, self.data['time_to_prepare'])
        self.assertEqual(dish.is_vegetarian, self.data['is_vegetarian'])
        self.assertEqual(dish.created, timezone.now())
        self.assertEqual(dish.updated, None)

    @freeze_time("2021-10-3")
    def test_update_dish(self):
        dish = DishFactory()
        serializer = DishSerializer(dish, data=self.data)
        serializer.is_valid(raise_exception=True)
        dish = serializer.save()

        self.assertEqual(dish.name, self.data['name'])
        self.assertEqual(dish.description, self.data['description'])
        self.assertEqual(dish.price, Decimal(self.data['price']))
        self.assertEqual(dish.time_to_prepare, self.data['time_to_prepare'])
        self.assertEqual(dish.is_vegetarian, self.data['is_vegetarian'])
        self.assertEqual(dish.created, timezone.now())
        self.assertEqual(dish.updated, timezone.now())
