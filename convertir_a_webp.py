from PIL import Image
import os

# Ruta a tu carpeta de imágenes
directorio = "/var/www/foodfusion/media"

# Extensiones que se van a convertir
extensiones = (".jpg", ".jpeg", ".png")

# Recorremos los archivos
for root, _, files in os.walk(directorio):
    for nombre_archivo in files:
        if nombre_archivo.lower().endswith(extensiones):
            ruta_original = os.path.join(root, nombre_archivo)
            ruta_webp = os.path.splitext(ruta_original)[0] + ".webp"

            try:
                with Image.open(ruta_original) as img:
                    img.save(ruta_webp, "webp", quality=80)
                    print(f"✅ Convertido: {ruta_webp}")
            except Exception as e:
                print(f"⚠️ Error al convertir {ruta_original}: {e}")
