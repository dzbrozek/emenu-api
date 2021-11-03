import datetime
from typing import List, cast

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from menus.models import Dish

from emenuapi.celery import app


def send_dish_report() -> bool:
    yesterday = (timezone.now() - datetime.timedelta(days=1)).date()

    new_dishes = Dish.objects.filter(created__date=yesterday)
    updated_dishes = Dish.objects.filter(updated__date=yesterday)

    if not new_dishes.exists() and not updated_dishes.exists():
        return False

    emails = cast(
        List[str], list(User.objects.filter(is_active=True).exclude(email='').values_list('email', flat=True))
    )

    if not emails:
        return False

    message = render_to_string('emails/dish_report.txt', {'new_dishes': new_dishes, 'updated_dishes': updated_dishes})

    return bool(
        send_mail(
            'Daily Dish Report',
            message,
            settings.FROM_EMAIL,
            emails,
            fail_silently=False,
        )
    )


@app.task
def report_dishes() -> None:
    send_dish_report()
    return
