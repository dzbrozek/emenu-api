import datetime

import pytz
from celery import states
from django.core import mail
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from freezegun import freeze_time
from menus.factories import DishFactory, UserFactory
from menus.models import Dish
from menus.tasks import report_dishes, send_dish_report


class ReportDishesTaskTest(TestCase):
    def test_run_task(self):
        result = report_dishes.apply()

        self.assertEqual(result.status, states.SUCCESS)
        self.assertEqual(result.get(), None)


@override_settings(FROM_EMAIL='from@localhost')
class SendDishReportTest(TestCase):
    def test_no_users(self):
        UserFactory(is_active=False, email='test@example.com')
        UserFactory(is_active=True, email='')
        DishFactory()

        self.assertEqual(send_dish_report(), 0)

        self.assertEqual(len(mail.outbox), 0)

    @freeze_time("2021-10-4")
    def test_no_new_dishes(self):
        UserFactory(is_active=True)
        DishFactory(
            created=datetime.datetime(2021, 10, 1, tzinfo=pytz.UTC),
            updated=datetime.datetime(2021, 10, 2, tzinfo=pytz.UTC),
        )
        self.assertEqual(send_dish_report(), 0)

        self.assertEqual(len(mail.outbox), 0)

    @freeze_time("2021-10-4")
    def test_new_dishes(self):
        user = UserFactory(is_active=True)
        UserFactory(is_active=True)
        DishFactory(
            created=datetime.datetime(2021, 10, 1, tzinfo=pytz.UTC),
        )
        dish = DishFactory(
            created=datetime.datetime(2021, 10, 3, 13, 30, tzinfo=pytz.UTC),
        )
        self.assertEqual(send_dish_report(), 2)

        self.assertEqual(len(mail.outbox), 2)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Daily Dish Report')
        self.assertEqual(email.to, [user.email])
        self.assertEqual(
            email.body,
            render_to_string(
                'emails/dish_report.txt',
                {'new_dishes': Dish.objects.filter(pk=dish.pk), 'updated_dishes': Dish.objects.none()},
            ),
        )

    @freeze_time("2021-10-4")
    def test_updated_dishes(self):
        user = UserFactory(is_active=True)
        dish = DishFactory(
            created=datetime.datetime(2021, 10, 1, tzinfo=pytz.UTC),
            updated=datetime.datetime(2021, 10, 3, 13, 30, tzinfo=pytz.UTC),
        )
        DishFactory(
            created=datetime.datetime(2021, 10, 2, tzinfo=pytz.UTC),
            updated=datetime.datetime(2021, 10, 2, 12, 30, tzinfo=pytz.UTC),
        )
        self.assertEqual(send_dish_report(), 1)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Daily Dish Report')
        self.assertEqual(email.to, [user.email])
        self.assertEqual(
            email.body,
            render_to_string(
                'emails/dish_report.txt',
                {'new_dishes': Dish.objects.none(), 'updated_dishes': Dish.objects.filter(pk=dish.pk)},
            ),
        )
