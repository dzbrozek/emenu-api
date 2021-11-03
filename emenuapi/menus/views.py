from django.db import models, transaction
from django.utils.functional import cached_property
from drf_spectacular.utils import extend_schema
from menus.models import Dish, Menu
from menus.serializers import DishSerializer, MenuSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


class MenuModelViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = MenuSerializer
    lookup_url_kwarg = 'menu_id'

    def get_queryset(self) -> models.QuerySet[Menu]:
        return Menu.objects.all().order_by('-created')

    @extend_schema(
        description='Returns list of menus',
    )
    def list(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().list(request, *args, *kwargs)

    @extend_schema(
        description='Creates a new menu',
    )
    def create(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().create(request, *args, *kwargs)

    @extend_schema(
        description='Retrieves a menu',
    )
    def retrieve(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().retrieve(request, *args, *kwargs)

    @extend_schema(
        description='Updates a menu',
    )
    def update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().update(request, *args, *kwargs)

    @extend_schema(
        description='Partially updates a menu',
    )
    def partial_update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().partial_update(request, *args, *kwargs)

    @extend_schema(
        description='Deletes a menu',
    )
    def destroy(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().destroy(request, *args, *kwargs)


class DishModelViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = DishSerializer
    lookup_url_kwarg = 'dish_id'

    @cached_property
    def menu(self) -> Menu:
        return Menu.objects.get(pk=self.kwargs['menu_menu_id'])

    def get_serializer_context(self) -> dict:
        context = super().get_serializer_context()
        context['menu'] = self.menu

        return context

    def get_queryset(self) -> models.QuerySet[Dish]:
        return Dish.objects.filter(menu_id=self.kwargs['menu_menu_id']).order_by('-created')

    @transaction.atomic
    def perform_destroy(self, instance: Dish) -> None:
        super().perform_destroy(instance)
        self.menu.update_last_updated()

    @extend_schema(
        description='Returns list of menu\'s dishes',
    )
    def list(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().list(request, *args, *kwargs)

    @extend_schema(
        description='Creates a new dish in a menu',
    )
    def create(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().create(request, *args, *kwargs)

    @extend_schema(
        description='Retrieves a dish from a menu',
    )
    def retrieve(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().retrieve(request, *args, *kwargs)

    @extend_schema(
        description='Updates a dish in a menu',
    )
    def update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().update(request, *args, *kwargs)

    @extend_schema(
        description='Partially updates a dish in a menu',
    )
    def partial_update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().partial_update(request, *args, *kwargs)

    @extend_schema(
        description='Deletes a dish from a menu',
    )
    def destroy(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().destroy(request, *args, *kwargs)


@extend_schema(
    description='Obtains auth token',
)
class ObtainAuthTokenAPIView(ObtainAuthToken):
    pass
