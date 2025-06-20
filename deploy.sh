#!/bin/bash

echo "🚀 Iniciando despliegue..."

# Ruta directa al Python del entorno virtual
PYTHON="/var/www/foodfusion/venv/bin/python"

cd /var/www/foodfusion

# Obtener los cambios
git pull origin pruebas

# Migraciones
$PYTHON manage.py migrate --noinput

# Archivos estáticos
$PYTHON manage.py collectstatic --noinput

# Reiniciar Gunicorn
sudo systemctl restart gunicorn

echo "✅ Despliegue finalizado."

