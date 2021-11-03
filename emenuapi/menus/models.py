from __future__ import annotations

from django.db import models
from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone


class MenuQuerySet(models.QuerySet):
    def with_num_dishes(self) -> models.QuerySet["Menu"]:
        dishes = Dish.objects.filter(menu=OuterRef('pk')).values('menu').annotate(num_dishes=Count('pk'))

        return super().annotate(num_dishes=Coalesce(Subquery(dishes.values('num_dishes')[:1]), 0))


class Menu(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    objects = MenuQuerySet.as_manager()

    def __str__(self) -> str:
        return f'Menu: {self.name}'

    def update_last_updated(self) -> None:
        self.updated = timezone.now()
        self.save()


class Dish(models.Model):
    menu = models.ForeignKey(Menu, related_name='dishes', on_delete=models.CASCADE)
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

    def __str__(self) -> str:
        return f'Dish: {self.name}'
