from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CategoriaMenu, Menu, Cliente, Mesa, Reserva, Empleado, Pedido, DetallePedido

admin.site.register(CategoriaMenu)
admin.site.register(Menu)
admin.site.register(Cliente)
admin.site.register(Mesa)
admin.site.register(Reserva)
admin.site.register(Empleado)
admin.site.register(Pedido)
admin.site.register(DetallePedido)