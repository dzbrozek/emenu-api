from django.test import TestCase
from menus.factories import DishFactory, MenuFactory
from menus.models import Menu


class MenuTest(TestCase):
    def test_with_num_dishes(self):
        first_menu, second_menu = MenuFactory.create_batch(2)
        first_menu.dishes.add(*DishFactory.create_batch(2))

        qs = Menu.objects.all().with_num_dishes()

        self.assertEqual(qs.get(pk=first_menu.pk).num_dishes, 2)
        self.assertEqual(qs.get(pk=second_menu.pk).num_dishes, 0)
