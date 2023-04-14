from django.contrib import admin

from catalog.models import Product, Category, SubCategory, ShoppingCart


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'name',
        'slug',
        'category',
        'sub_category',
        'image',
        'price',
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'image',
    )

@admin.register(SubCategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'category',
        'image',
    )

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'buyer',
        'product',
        'amount',
        'get_total',
    )
