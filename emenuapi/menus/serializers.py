from typing import cast

from django.db import transaction
from django.utils import timezone
from menus.models import Dish, Menu
from rest_framework import serializers


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('id', 'name', 'description', 'created', 'updated')
        read_only_fields = ('created', 'updated')

    def update(self, instance: Menu, validated_data: dict) -> Menu:
        data = {**validated_data, 'updated': timezone.now()}
        return cast(Menu, super().update(instance, data))


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ('id', 'name', 'description', 'price', 'time_to_prepare', 'is_vegetarian', 'created', 'updated')
        read_only_fields = ('created', 'updated')

    @transaction.atomic
    def create(self, validated_data: dict) -> Dish:
        data = {**validated_data, 'menu': self.context['menu']}
        dish = super().create(data)
        self.context['menu'].update_last_updated()
        return cast(Dish, dish)

    @transaction.atomic
    def update(self, instance: Dish, validated_data: dict) -> Dish:
        data = {**validated_data, 'updated': timezone.now()}
        dish = super().update(instance, data)
        self.context['menu'].update_last_updated()
        return cast(Dish, dish)
