import datetime

import pytz
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from menus.factories import DishFactory, MenuFactory, UserFactory
from menus.models import Dish, Menu
from menus.serializers import DishSerializer, MenuDetailsSerializer, MenuSerializer
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
        self.first_menu, self.second_menu = MenuFactory.create_batch(2)
        self.first_menu.dishes.add(DishFactory())

    def test_unauthenticated_user_cannot_retrieve_empty_menu(self):
        response = self.client.get(reverse('menus:menu-detail', kwargs=dict(menu_id=self.second_menu.pk)))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': 'Not found.'})

    def test_unauthenticated_user_can_retrieve_non_empty_menu(self):
        response = self.client.get(reverse('menus:menu-detail', kwargs=dict(menu_id=self.first_menu.pk)))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), MenuDetailsSerializer(self.first_menu).data)

    def test_authenticated_user_can_retrieve_menu(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.get(reverse('menus:menu-detail', kwargs=dict(menu_id=self.second_menu.pk)))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), MenuDetailsSerializer(self.second_menu).data)


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
        self.first_menu = MenuFactory(
            name='First menu for breakfast',
            created=datetime.datetime(2021, 5, 1, 12, 13, tzinfo=pytz.UTC),
            updated=datetime.datetime(2021, 6, 1, 12, 13, tzinfo=pytz.UTC),
        )
        self.second_menu = MenuFactory(
            name='Second menu for lunch',
            created=datetime.datetime(2021, 5, 5, 6, 30, tzinfo=pytz.UTC),
            updated=datetime.datetime(2021, 6, 5, 6, 30, tzinfo=pytz.UTC),
        )
        self.third_menu = MenuFactory(
            name='Third menu for dinner',
            created=datetime.datetime(2021, 5, 15, 16, 16, tzinfo=pytz.UTC),
            updated=datetime.datetime(2021, 6, 15, 16, 16, tzinfo=pytz.UTC),
        )
        self.first_menu.dishes.add(*DishFactory.create_batch(2))
        self.second_menu.dishes.add(DishFactory())

    def test_unauthenticated_user_can_list_non_empty_menus(self):
        response = self.client.get(reverse('menus:menu-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), MenuSerializer([self.second_menu, self.first_menu], many=True).data)

    def test_authenticated_user_can_list_menu(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.get(reverse('menus:menu-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), MenuSerializer([self.third_menu, self.second_menu, self.first_menu], many=True).data
        )

    def test_sort_list_by_name(self):
        response = self.client.get(f"{reverse('menus:menu-list')}?ordering=-name")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), MenuSerializer([self.second_menu, self.first_menu], many=True).data)

        response = self.client.get(f"{reverse('menus:menu-list')}?ordering=name")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), MenuSerializer([self.first_menu, self.second_menu], many=True).data)

    def test_sort_list_by_num_dishes(self):
        response = self.client.get(f"{reverse('menus:menu-list')}?ordering=-num_dishes")

        self.assertEqual(response.json(), MenuSerializer([self.first_menu, self.second_menu], many=True).data)

        response = self.client.get(f"{reverse('menus:menu-list')}?ordering=num_dishes")

        self.assertEqual(response.json(), MenuSerializer([self.second_menu, self.first_menu], many=True).data)

    def test_filter_list_by_name(self):
        response = self.client.get(f"{reverse('menus:menu-list')}?search=lunch")

        self.assertEqual(response.json(), MenuSerializer([self.second_menu], many=True).data)

    def test_filter_list_by_created(self):
        after = datetime.datetime(2021, 5, 5, tzinfo=pytz.UTC)
        before = datetime.datetime(2021, 5, 10, tzinfo=pytz.UTC)

        response = self.client.get(
            f"{reverse('menus:menu-list')}?created_after={after.isoformat().replace('+00:00', '')}&created_before={before.isoformat().replace('+00:00', '')}"
        )

        self.assertEqual(response.json(), MenuSerializer([self.second_menu], many=True).data)

    def test_filter_list_by_updated(self):
        after = datetime.datetime(2021, 5, 30, tzinfo=pytz.UTC)
        before = datetime.datetime(2021, 6, 2, tzinfo=pytz.UTC)

        response = self.client.get(
            f"{reverse('menus:menu-list')}?updated_after={after.isoformat().replace('+00:00', '')}&updated_before={before.isoformat().replace('+00:00', '')}"
        )

        self.assertEqual(response.json(), MenuSerializer([self.first_menu], many=True).data)


class CreateDishTest(APITestCase):
    def setUp(self):
        self.data = {
            'name': 'Test dish',
            'description': 'Test dish description',
            'price': '24.99',
            'time_to_prepare': 30,
            'is_vegetarian': False,
        }

    def test_unauthenticated_user_cannot_create_dish(self):
        response = self.client.post(reverse('menus:dish-list'), data=self.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_create_dish(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.post(reverse('menus:dish-list'), data=self.data)

        dish = Dish.objects.get()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), DishSerializer(dish).data)


class RetrieveDishTest(APITestCase):
    def setUp(self):
        self.dish = DishFactory()

    def test_unauthenticated_user_cannot_retrieve_dish(self):
        response = self.client.get(reverse('menus:dish-detail', kwargs=dict(dish_id=self.dish.pk)))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_retrieve_dish(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.get(reverse('menus:dish-detail', kwargs=dict(dish_id=self.dish.pk)))

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
            reverse('menus:dish-detail', kwargs=dict(dish_id=self.dish.pk)),
            data=self.data,
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_update_dish(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.put(
            reverse('menus:dish-detail', kwargs=dict(dish_id=self.dish.pk)),
            data=self.data,
        )

        self.dish.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), DishSerializer(self.dish).data)


class DestroyDishTest(APITestCase):
    def setUp(self):
        self.dish = DishFactory()

    def test_unauthenticated_user_cannot_delete_dish(self):
        response = self.client.delete(
            reverse('menus:dish-detail', kwargs=dict(dish_id=self.dish.pk)),
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    @freeze_time("2021-10-3")
    def test_authenticated_user_can_delete_dish(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.delete(
            reverse('menus:dish-detail', kwargs=dict(dish_id=self.dish.pk)),
        )

        self.assertEqual(response.status_code, 204)

        with self.assertRaises(Dish.DoesNotExist):
            self.dish.refresh_from_db()


class ListDishTest(APITestCase):
    def setUp(self):
        self.first_dish, self.second_dish = DishFactory.create_batch(2)

    def test_unauthenticated_user_cannot_list_dishes(self):
        response = self.client.get(
            reverse('menus:dish-list'),
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_list_dishes(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.get(
            reverse('menus:dish-list'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), DishSerializer([self.second_dish, self.first_dish], many=True).data)


@freeze_time("2021-10-3")
class UploadDishPhotoTest(APITestCase):
    def setUp(self):
        self.dish = DishFactory(image='')
        image = SimpleUploadedFile("image.png", b"image_content", content_type="image/png")
        self.data = {'file': image}

    def test_unauthenticated_user_cannot_upload_photo(self):
        response = self.client.post(
            reverse('menus:dish-photo', kwargs=dict(dish_id=self.dish.pk)),
            data=self.data,
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_user_can_upload_photo(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.post(
            reverse('menus:dish-photo', kwargs=dict(dish_id=self.dish.pk)),
            data=self.data,
        )

        self.dish.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), DishSerializer(self.dish).data)

        self.assertTrue(self.dish.image.name)
        self.assertEqual(self.dish.updated, timezone.now())
