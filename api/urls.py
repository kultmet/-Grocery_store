from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from api.views import ProductViewSet, CategoryViewSet, SubCategoryViewSet#, shopping_cart

router = DefaultRouter()

router.register(r'products', ProductViewSet, basename='products')
router.register(r'categiries', CategoryViewSet, basename='categiries')
router.register(r'sub_categiries', SubCategoryViewSet, basename='sub_categiries')

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('v1/', include(router.urls)),
    # path('v1/shopping_cart/', shopping_cart, name='shopping_cart'),
]