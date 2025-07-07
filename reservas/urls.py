from django.urls import path
from django.urls import path, include
from . import views1
urlpatterns = [
    path('', views1.inicio, name='inicio'),
    path('menus/', views1.menus, name='menus'),
    path('api/menus-filtrados/', views1.menus_filtrados_json, name='menus_filtrados_json'),  # <-- nueva ruta API
    path('signup/', views1.registro_cliente, name='registro_cliente'),
    path('login/', views1.login_cliente, name='login_cliente'),
    path('logout/', views1.signout_cliente, name='logout_cliente'),
    path('mis_datos/', views1.mis_datos, name='mis_datos'),
    path('mesas/', views1.mesas_disponibles, name='mesas_disponibles'),
    path('reservar/<int:mesa_id>/', views1.reservar_mesa, name='reservar_mesa'),
    path('mis-reservas/cancelar/<int:reserva_id>/', views1.cancelar_reserva, name='cancelar_reserva'),
    
    path('mis-reservas/', views1.mis_reservas, name='mis_reservas'),
    path('', include('pwa.urls')),  # debe ir al finalv
    
]
#path('eliminar-cuenta/', views.eliminar_cuenta, name='eliminar_cuenta'),