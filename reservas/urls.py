from django.urls import path

from restaurante_reservas import settings # type: ignore
from . import views
from django.conf.urls.static import static
urlpatterns = [

    path('', views.inicio, name='inicio'),
    path('menu/', views.menus, name='menu'),
    path('signup/', views.registro, name='registro'),
    path('login/', views.login, name='login'),
    path('logout/', views.signout, name='logout'),
    path('mis_datos/', views.mis_datos, name='mis_datos'),
    path('mesas/', views.mesas_disponibles, name='mesas_disponibles'),
    path('reservar/<int:mesa_id>/', views.reservar_mesa, name='reservar_mesa'),
    path('eliminar-cuenta/', views.eliminar_cuenta, name='eliminar_cuenta'),
    path('editar_datos/', views.editar_datos, name='editar_datos'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
