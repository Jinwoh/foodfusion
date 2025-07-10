from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os
from .models import Menu

@receiver(post_save, sender=Menu)
def convertir_a_webp(sender, instance, created, **kwargs):
    if instance.img_url and not instance.img_url.name.endswith('.webp'):
        ruta_original = instance.img_url.path
        ruta_webp = os.path.splitext(ruta_original)[0] + ".webp"

        try:
            # Convertir imagen
            imagen = Image.open(ruta_original).convert("RGB")
            imagen.save(ruta_webp, "webp")

            # Evitar bucle infinito usando update()
            Menu.objects.filter(pk=instance.pk).update(
                img_url=os.path.relpath(ruta_webp, start=os.path.join(os.getcwd(), 'media'))
            )

            # Eliminar la imagen original
            if os.path.exists(ruta_original):
                os.remove(ruta_original)

        except Exception as e:
            print(f"❌ Error al convertir imagen a WebP: {e}")

