
from datetime import datetime
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import ImageField

from PIL import Image as PillowImage, ImageOps

User = get_user_model()

class Common(models.Model):
    name = models.CharField(max_length=100, verbose_name='name')
    slug = models.SlugField(verbose_name='slug')

    class Meta:
        abstract = True
    
    def __str__(self) -> str:
        return self.name

class Category(Common):
    """Model for product Categories."""
    image = models.ImageField(upload_to='catigories')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    

class SubCategory(Common):
    """Model for product Sub-Categories."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    image = models.ImageField(upload_to='sub_catigories')

    class Meta:
        verbose_name = 'Sub-Category'
        verbose_name_plural = 'Sub-Categories'


def folder_path(instance, filename):
    """Генерирует имя файла. Возвращает путь к нему."""
    return (
        f'products/{instance.slug}_'
        f'{datetime.now().timestamp()*1000:.0f}.jpg'
    )

class Product(Common):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to=folder_path)
    price = models.FloatField(verbose_name='price')

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    
    def thumbnail_generator(self, infile, outfile, image_size):
        """Генерирует изображения в требуемых размерах."""
        with PillowImage.open(infile) as im:
            im.thumbnail(image_size)
            ImageOps.fit(
                im, image_size, PillowImage.Resampling.LANCZOS, 0.5
            ).save(outfile, quality=95)

    def filename_generator(self, filepath, size):
        """Генерирует имя для каждого размера изображения."""
        width, height = size
        name, file_format = filepath.split('.')
        return f'{name}_{width}x{height}.{file_format}'

    def save(self, *args, **kwargs):
        """Сохраняет дополнительно изображения в требуемых размерах."""
        super(Product, self).save(*args, **kwargs)
        for size in settings.PREVIEW_SIZES:
            self.thumbnail_generator(
                infile=self.image,
                outfile=self.filename_generator(self.image.path, size),
                image_size=size,
            )

    def delete_thumbnails(self):
        """Удаляет дополнительно все файлы связанные с объектом."""
        for size in settings.PREVIEW_SIZES:
            file_name = self.filename_generator(self.image.path, size)
            if os.path.exists(file_name):
                os.remove(file_name)


class ShoppingCart(models.Model):
    """Shopping cart for User."""
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='carts')
    amount = models.PositiveIntegerField('amount', default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['buyer', 'product'],
                name='Unique product with buyer',
            )
        ]

    def get_total(self):
        return self.product.price * self.amount

