from typing import cast

from django.utils import timezone
from menus.models import Dish, Menu
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = (
            'id',
            'name',
            'description',
            'price',
            'time_to_prepare',
            'is_vegetarian',
            'image',
            'created',
            'updated',
        )
        read_only_fields = ('created', 'updated', 'image')

    def create(self, validated_data: dict) -> Dish:
        data = {**validated_data}
        dish = super().create(data)
        return cast(Dish, dish)

    def update(self, instance: Dish, validated_data: dict) -> Dish:
        data = {**validated_data, 'updated': timezone.now()}
        dish = super().update(instance, data)
        return cast(Dish, dish)


class MenuSerializer(serializers.ModelSerializer):
    dishes = PrimaryKeyRelatedField(queryset=Dish.objects.all(), many=True)

    class Meta:
        model = Menu
        fields = ('id', 'name', 'description', 'dishes', 'created', 'updated')
        read_only_fields = ('created', 'updated')

    def update(self, instance: Menu, validated_data: dict) -> Menu:
        data = {**validated_data, 'updated': timezone.now()}
        return cast(Menu, super().update(instance, data))


class MenuDetailsSerializer(serializers.ModelSerializer):
    dishes = DishSerializer(many=True)

    class Meta:
        model = Menu
        fields = ('id', 'name', 'description', 'dishes', 'created', 'updated')
