from __future__ import annotations

from decimal import Decimal
from typing import cast

from django.db import models
from django.db.models import Count


class MenuQuerySet(models.QuerySet):
    def with_num_dishes(self) -> models.QuerySet["Menu"]:
        return cast(models.QuerySet["Menu"], super().prefetch_related('dishes').annotate(num_dishes=Count('dishes')))


class Menu(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)
    dishes = models.ManyToManyField('menus.Dish', blank=True)

    objects = MenuQuerySet.as_manager()

    def __str__(self) -> str:
        return f'Menu: {self.name}'


class Dish(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    time_to_prepare = models.PositiveIntegerField(help_text='Time in minutes')
    is_vegetarian = models.BooleanField()
    image = models.ImageField(upload_to='menus/dish', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Dishes'
        constraints = [
            models.CheckConstraint(check=models.Q(price__gt=Decimal('0')), name='dish_price_positive'),
        ]

    def __str__(self) -> str:
        return f'Dish: {self.name}'
