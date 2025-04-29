from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.registro, name='registro'),
    path('login/', views.login, name='login'),
    path('menus/', views.menus, name='menus'),
    path('logout/', views.signout, name='logout'),
    path('mis_datos/', views.mis_datos, name='mis_datos'),
    path('mesas/', views.mesas_disponibles, name='mesas_disponibles'),
    path('reservar/<int:mesa_id>/', views.reservar_mesa, name='reservar_mesa'),
]
