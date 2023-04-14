from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, F
from django.core.validators import MinValueValidator, MaxValueValidator

from rest_framework import serializers
from rest_framework.validators import ValidationError
from rest_framework.generics import get_object_or_404

from catalog.models import *

User = get_user_model()


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product."""
    sub_category = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    class Meta:
        model = Product
        fields = (
            'pk',
            'name',
            'slug',
            'category',
            'sub_category',
            'image',
            'price',
        )
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class SubCategorySerializer(serializers.ModelSerializer):
    """Serializer for Sub-Category."""
    category = serializers.StringRelatedField()
    class Meta:
        model = SubCategory
        fields = (
            'name',
            'slug',
            'category',
            'image',
        )


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Gategory."""
    sub_categories = SubCategorySerializer(source='subcategories', many=True)
    class Meta:
        model = Category
        fields = (
            'name',
            'slug',
            'image',
            'sub_categories'
        )


class ShortShoppingCartSerializer(serializers.ModelSerializer):
    """Getting every entry. This is auxiliary serializer."""
    product = serializers.StringRelatedField()
    price = serializers.SerializerMethodField()
    class Meta:
        model = ShoppingCart
        fields = ('product', 'price', 'amount')
    
    def get_price(self, obj):
        return obj.product.price


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Serializer for getting all entries from the ShoppingCart 
    as well as total amount products and total price.
    """
    products = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField(method_name='get_total_amount')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('products', 'total_amount', 'total_price')
    
    def __init__(self, instance, **kwargs):
        print(type(instance))
        super().__init__(instance, **kwargs)
        self.queryset = ShoppingCart.objects.filter(buyer=self.instance)
        self.aggregated_data = self.queryset.aggregate(total_amount=Sum('amount'), total_price=Sum(F('product__price')*F('amount')))
    
    def get_total_amount(self, obj):
        return self.aggregated_data['total_amount']
    
    def get_products(self, obj):
        instance = self.queryset
        serializer = ShortShoppingCartSerializer(instance, many=True)
        return serializer.data
    
    def get_total_price(self, obj):
        return self.aggregated_data['total_price']


class CreateShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for create update and delete ShoppingCart entry."""
    amount = serializers.IntegerField(validators=[
        MinValueValidator(
            limit_value=1,
            message='Must be positive! Not less 1'
        ),
        MaxValueValidator(
            limit_value=10000,
            message='Well!!! Too much! No greater than 10000'
        )
    ])
    class Meta:
        model = ShoppingCart
        fields = ('buyer', 'product', 'amount')

    def to_internal_value(self, data):
        product = Product.objects.get(slug=data['product'])
        data['buyer'] = data['buyer'].id
        data['product'] = product.pk
        return super().to_internal_value(data)

    def validate(self, attrs):
        try:
            request = self.context['request']
            buyer = attrs['buyer']
            product = attrs['product']
            attrs['amount']
        except KeyError:
            raise ValidationError('KeyError')
        if request.method == 'POST':
            if ShoppingCart.objects.filter(buyer=buyer, product=product).exists():
                raise ValidationError(
                    f'У вас в корзине уже есть {product.name}!'
                )
        if request.method in ('DELETE', 'PATCH'):
            if not ShoppingCart.objects.filter(buyer=buyer, product=product).exists():
                raise ValidationError(
                    'В корзине нет этого!'
                )
        return super().validate(attrs)

    def update(self, instance, validated_data):
        entry = ShoppingCart.objects.get(buyer=validated_data['buyer'], product=validated_data['product'])
        entry.amount = validated_data['amount']
        entry.product = validated_data['product']
        entry.save()
        return entry
