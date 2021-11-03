from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from menus.factories import DishFactory, MenuFactory, UserFactory
from menus.models import Dish, Menu
from menus.serializers import DishSerializer, MenuSerializer
from rest_framework.test import APITestCase


class CreateMenuTest(APITestCase):
    def setUp(self):
        self.data = {'name': 'Test menu', 'description': 'Test description'}

    def test_unauthenticated_user_cannot_create_menu(self):
        response = self.client.post(reverse('menus:menu-list'), data=self.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_create_menu(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.post(reverse('menus:menu-list'), data=self.data)

        menu = Menu.objects.get()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), MenuSerializer(menu).data)


class RetrieveMenuTest(APITestCase):
    def setUp(self):
        self.menu = MenuFactory()

    def test_unauthenticated_user_cannot_retrieve_menu(self):
        response = self.client.get(reverse('menus:menu-detail', kwargs=dict(menu_id=self.menu.pk)))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_retrieve_menu(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.get(reverse('menus:menu-detail', kwargs=dict(menu_id=self.menu.pk)))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), MenuSerializer(self.menu).data)


class UpdateMenuTest(APITestCase):
    def setUp(self):
        self.menu = MenuFactory()
        self.data = {'name': 'Test menu', 'description': 'Test description'}

    def test_unauthenticated_user_cannot_update_menu(self):
        response = self.client.put(reverse('menus:menu-detail', kwargs=dict(menu_id=self.menu.pk)), data=self.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_update_menu(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.put(reverse('menus:menu-detail', kwargs=dict(menu_id=self.menu.pk)), data=self.data)

        self.menu.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), MenuSerializer(self.menu).data)


class DestroyMenuTest(APITestCase):
    def setUp(self):
        self.menu = MenuFactory()

    def test_unauthenticated_user_cannot_delete_menu(self):
        response = self.client.delete(reverse('menus:menu-detail', kwargs=dict(menu_id=self.menu.pk)))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_delete_menu(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.delete(reverse('menus:menu-detail', kwargs=dict(menu_id=self.menu.pk)))

        self.assertEqual(response.status_code, 204)

        with self.assertRaises(Menu.DoesNotExist):
            self.menu.refresh_from_db()


class ListMenuTest(APITestCase):
    def setUp(self):
        self.first_menu, self.second_menu = MenuFactory.create_batch(2)

    def test_unauthenticated_user_cannot_list_menu(self):
        response = self.client.get(reverse('menus:menu-list'))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_list_menu(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.get(reverse('menus:menu-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), MenuSerializer([self.second_menu, self.first_menu], many=True).data)


class CreateDishTest(APITestCase):
    def setUp(self):
        self.menu = MenuFactory()
        self.data = {
            'name': 'Test dish',
            'description': 'Test dish description',
            'price': '24.99',
            'time_to_prepare': 30,
            'is_vegetarian': False,
        }

    def test_unauthenticated_user_cannot_create_dish(self):
        response = self.client.post(reverse('menus:dish-list', kwargs=dict(menu_menu_id=self.menu.pk)), data=self.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_create_dish(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.post(reverse('menus:dish-list', kwargs=dict(menu_menu_id=self.menu.pk)), data=self.data)

        dish = Dish.objects.get(menu=self.menu)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), DishSerializer(dish).data)


class RetrieveDishTest(APITestCase):
    def setUp(self):
        self.dish = DishFactory()

    def test_unauthenticated_user_cannot_retrieve_dish(self):
        response = self.client.get(
            reverse('menus:dish-detail', kwargs=dict(menu_menu_id=self.dish.menu_id, dish_id=self.dish.pk))
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_retrieve_dish(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.get(
            reverse('menus:dish-detail', kwargs=dict(menu_menu_id=self.dish.menu_id, dish_id=self.dish.pk))
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), DishSerializer(self.dish).data)


class UpdateDishTest(APITestCase):
    def setUp(self):
        self.dish = DishFactory()
        self.data = {
            'name': 'Test dish',
            'description': 'Test dish description',
            'price': '24.99',
            'time_to_prepare': 30,
            'is_vegetarian': False,
        }

    def test_unauthenticated_user_cannot_update_dish(self):
        response = self.client.put(
            reverse('menus:dish-detail', kwargs=dict(menu_menu_id=self.dish.menu_id, dish_id=self.dish.pk)),
            data=self.data,
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_update_dish(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.put(
            reverse('menus:dish-detail', kwargs=dict(menu_menu_id=self.dish.menu_id, dish_id=self.dish.pk)),
            data=self.data,
        )

        self.dish.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), DishSerializer(self.dish).data)


class DestroyDishTest(APITestCase):
    def setUp(self):
        self.menu = MenuFactory()
        self.dish = DishFactory(menu=self.menu)

    def test_unauthenticated_user_cannot_delete_dish(self):
        response = self.client.delete(
            reverse('menus:dish-detail', kwargs=dict(menu_menu_id=self.dish.menu_id, dish_id=self.dish.pk)),
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    @freeze_time("2021-10-3")
    def test_authenticated_user_can_delete_dish(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.delete(
            reverse('menus:dish-detail', kwargs=dict(menu_menu_id=self.dish.menu_id, dish_id=self.dish.pk)),
        )

        self.assertEqual(response.status_code, 204)

        with self.assertRaises(Dish.DoesNotExist):
            self.dish.refresh_from_db()

        self.menu.refresh_from_db()
        self.assertEqual(self.menu.updated, timezone.now())


class ListDishTest(APITestCase):
    def setUp(self):
        self.menu = MenuFactory()
        self.first_dish, self.second_dish = DishFactory.create_batch(2, menu=self.menu)
        DishFactory()

    def test_unauthenticated_user_cannot_list_dishes(self):
        response = self.client.get(
            reverse('menus:dish-list', kwargs=dict(menu_menu_id=self.menu.pk)),
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_list_dishes(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.get(
            reverse('menus:dish-list', kwargs=dict(menu_menu_id=self.menu.pk)),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), DishSerializer([self.second_dish, self.first_dish], many=True).data)
