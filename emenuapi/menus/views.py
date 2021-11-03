from typing import cast

from django.db import models, transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from menus.filters import MenuFilter
from menus.models import Dish, Menu
from menus.serializers import DishSerializer, MenuDetailsSerializer, MenuSerializer
from rest_framework import filters
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


class MenuModelViewSet(ModelViewSet):
    lookup_url_kwarg = 'menu_id'
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    ordering_fields = ['name', 'num_dishes']
    search_fields = ['name']
    filterset_class = MenuFilter

    def get_queryset(self) -> models.QuerySet["Menu"]:
        qs = cast(models.QuerySet["Menu"], Menu.objects.with_num_dishes().order_by('-created'))  # type: ignore
        if self.request.user and self.request.user.is_authenticated:
            return qs
        return qs.filter(num_dishes__gt=0)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MenuDetailsSerializer
        return MenuSerializer

    @extend_schema(
        description='Returns list of menus',
        parameters=[
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Order results',
                enum=["name", "-name", "num_dishes", "-num_dishes"],
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter results by name',
            ),
        ],
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
    queryset = Dish.objects.none()

    def get_queryset(self) -> models.QuerySet[Dish]:
        return Dish.objects.all().order_by('-created')

    @extend_schema(
        description='Returns list of dishes',
    )
    def list(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().list(request, *args, *kwargs)

    @extend_schema(
        description='Creates a new dish',
    )
    def create(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().create(request, *args, *kwargs)

    @extend_schema(
        description='Retrieves a dish',
    )
    def retrieve(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().retrieve(request, *args, *kwargs)

    @extend_schema(
        description='Updates a dish',
    )
    def update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().update(request, *args, *kwargs)

    @extend_schema(
        description='Partially updates a dish',
    )
    def partial_update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().partial_update(request, *args, *kwargs)

    @extend_schema(
        description='Deletes a dish',
    )
    def destroy(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().destroy(request, *args, *kwargs)

    @extend_schema(
        description='Uploads a dish photo',
        operation_id='upload_file',
        request={
            'multipart/form-data': {'type': 'object', 'properties': {'file': {'type': 'string', 'format': 'binary'}}}
        },
    )
    @transaction.atomic()
    @action(detail=True, methods=['post'])
    def photo(self, request, *args, **kwargs):
        dish = self.get_object()
        try:
            image = request.data['file']
            dish.image = image
            dish.updated = timezone.now()
            dish.save()
        except KeyError:
            raise ParseError('Request has no resource file attached')

        return Response(DishSerializer(dish).data)


@extend_schema(
    description='Obtains auth token',
)
class ObtainAuthTokenAPIView(ObtainAuthToken):
    pass
