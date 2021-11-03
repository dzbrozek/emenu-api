from django.db import models
from django.utils import timezone


class Menu(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f'Menu: {self.name}'

    def update_last_updated(self) -> None:
        self.updated = timezone.now()
        self.save()


class Dish(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    time_to_prepare = models.PositiveIntegerField(help_text='Time in minutes')
    is_vegetarian = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Dishes'

    def __str__(self) -> str:
        return f'Dish: {self.name}'
