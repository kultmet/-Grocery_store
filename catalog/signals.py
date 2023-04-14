from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from catalog.models import Product


@receiver(post_delete, sender=Product)
def image_post_delete(sender, instance, **kwargs):
    """Удаляет файлы превьюшек при удалении изображения."""
    instance.delete_thumbnails()


@receiver(pre_save, sender=Product)
def update_thumbnails(sender, instance, **kwargs):
    """Обновляет файлы превьюшек при обновлении изображения."""
    if not instance.pk:
        # Это скорее всего новое изображение, не обновляем превьюшки
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # Это все-таки новое изображение, не обновляем превьюшки
        return
    if old_instance.image != instance.image:
        # Изображение было обновлено, удаляем старые превьюшки
        old_instance.delete_thumbnails()
