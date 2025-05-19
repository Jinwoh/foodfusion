from django.urls import path
from . import views
urlpatterns = [

    path('', views.inicio, name='inicio'),
    path('menus/', views.menus, name='menus'),
    path('signup/', views.registro, name='registro'),
    path('login/', views.login, name='login'),
    path('logout/', views.signout, name='logout'),
    path('mis_datos/', views.mis_datos, name='mis_datos'),
    path('mesas/', views.mesas_disponibles, name='mesas_disponibles'),
    path('reservar/<int:mesa_id>/', views.reservar_mesa, name='reservar_mesa'),
    path('mis-reservas/cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('eliminar-cuenta/', views.eliminar_cuenta, name='eliminar_cuenta'),
    path('editar_datos/', views.editar_datos, name='editar_datos'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
]
