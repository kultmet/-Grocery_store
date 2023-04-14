from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from catalog.models import Product, Category, SubCategory, ShoppingCart
from api.serializers import ProductSerializer, CategorySerializer, SubCategorySerializer, ShoppingCartSerializer, CreateShoppingCartSerializer
from api.paginators import CustomPaginator



User = get_user_model()

class ProductViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """ViewSet for Products."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    pagination_class = CustomPaginator

    @action(
            methods=['POST', 'PATCH', 'DELETE'],
            detail=True,
            url_path='edit_cart',
            url_name='edit_cart',
            serializer_class=CreateShoppingCartSerializer
    )
    def edit_cart(self, request, slug):
        """
        This action allows you to create, 
        uplate and remove entry in the ShoppingCart.
        """
        request.data['request'] = request
        request.data['buyer'] = request.user
        request.data['product'] = slug
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            print(serializer.validated_data)
            ShoppingCart.objects.create(
                **serializer.validated_data
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        if request.method == 'PATCH':
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            return Response(serializer.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        buyer = serializer.validated_data['buyer']
        product = serializer.validated_data['product']
        order = get_object_or_404(ShoppingCart, buyer=buyer, product=product)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET', 'DELETE',],
        detail=False,
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(IsAuthenticated,),
        serializer_class=ShoppingCartSerializer
    )
    def shopping_cart(self, request):
        """
        This action allows you to view all entntries 
        in the ShoppingCart or clean its.
        """
        buyer = request.user
        if request.method == 'GET':
            instance = User.objects.get(username=request.user.username)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        queryset = ShoppingCart.objects.filter(buyer=buyer)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """ViewSet for Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPaginator


class SubCategoryViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """ViewSet for Sub-Category."""
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    pagination_class = CustomPaginator
