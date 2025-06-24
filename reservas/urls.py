from django.urls import path
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('menus/', views.menus, name='menus'),
    path('api/menus-filtrados/', views.menus_filtrados_json, name='menus_filtrados_json'),  # <-- nueva ruta API
    path('signup/', views.registro_cliente, name='registro_cliente'),
    path('acceso/', views.login_cliente, name='login_cliente'),
    path('cerrar_sesion/', views.signout_cliente, name='logout_cliente'),
    path('mis_datos/', views.mis_datos, name='mis_datos'),
    path('mesas/', views.mesas_disponibles, name='mesas_disponibles'),
    path('reservar/<int:mesa_id>/', views.reservar_mesa, name='reservar_mesa'),
    path('mis-reservas/cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('eliminar-cuenta/', views.eliminar_cuenta, name='eliminar_cuenta'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('', include('pwa.urls')),  # debe ir al finalv
    
]
