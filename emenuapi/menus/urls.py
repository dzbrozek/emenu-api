from menus.views import DishModelViewSet, MenuModelViewSet
from rest_framework.routers import DefaultRouter

app_name = 'menus'

router = DefaultRouter()
router.register(r'menus', MenuModelViewSet, basename='menu')
router.register(r'dishes', DishModelViewSet, basename='dish')

urlpatterns = router.urls
