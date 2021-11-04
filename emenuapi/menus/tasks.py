import datetime
import logging
from typing import List, cast

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.utils import timezone
from menus.models import Dish

from emenuapi.celery import app

logger = logging.getLogger(__name__)


def send_dish_report() -> int:
    logger.info("Sending emails for daily dish report")
    yesterday = (timezone.now() - datetime.timedelta(days=1)).date()

    new_dishes = Dish.objects.filter(created__date=yesterday)
    updated_dishes = Dish.objects.filter(updated__date=yesterday)

    if not new_dishes.exists() and not updated_dishes.exists():
        logger.info('No new or updated dishes to report. Daily report not sent')
        return 0

    recipient_list = cast(
        List[str],
        list(User.objects.filter(is_active=True).exclude(email='').order_by('id').values_list('email', flat=True)),
    )

    if not recipient_list:
        logger.info('Empty recipient list. Daily report not sent')
        return 0

    if not settings.FROM_EMAIL:
        logger.info('"FROM_EMAIL" not set. Daily report not sent')
        return 0

    message = render_to_string('emails/dish_report.txt', {'new_dishes': new_dishes, 'updated_dishes': updated_dishes})
    messages = [('Daily Dish Report', message, settings.FROM_EMAIL, [recipient]) for recipient in recipient_list]

    emails_sent = send_mass_mail(messages)

    logger.info('Sent %d emails for daily dish report', emails_sent)

    return emails_sent


@app.task
def report_dishes() -> None:
    send_dish_report()
    return
