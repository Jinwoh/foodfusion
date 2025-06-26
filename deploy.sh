#!/bin/bash

echo "🚀 Iniciando despliegue de FoodFusion..."

# Ir al directorio del proyecto
cd /var/www/foodfusion

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Obtener últimos cambios del repositorio
echo "⬇️ Haciendo pull de los últimos cambios..."
git pull origin master

# Aplicar migraciones (por si se cambió la base de datos)
echo "🔧 Aplicando migraciones..."
python manage.py migrate

# Recolectar archivos estáticos (script.js, CSS, imágenes)
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Reiniciar Gunicorn para aplicar cambios en producción
echo "♻️ Reiniciando Gunicorn..."
sudo systemctl restart gunicorn

echo "✅ Despliegue completado con éxito."

