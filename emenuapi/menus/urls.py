from menus.views import DishModelViewSet, MenuModelViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

app_name = 'menus'

router = DefaultRouter()
router.register(r'menus', MenuModelViewSet, basename='menu')

menu_router = routers.NestedSimpleRouter(router, r'menus', lookup='menu')
menu_router.register(r'dishes', DishModelViewSet, basename='dish')

urlpatterns = router.urls + menu_router.urls
