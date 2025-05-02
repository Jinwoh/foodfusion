from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CategoriaMenu, Menu, Cliente, Mesa, Reserva, Empleado, Pedido, DetallePedido


from .models import ClienteHistorial

@admin.register(ClienteHistorial)
class ClienteHistorialAdmin(admin.ModelAdmin):
    list_display = ('nombre_apellido', 'correo', 'cedula', 'telefono', 'fecha_registro', 'fecha_eliminacion')
    search_fields = ('correo', 'cedula', 'nombre_apellido')
    list_filter = ('fecha_eliminacion',)

    
admin.site.site_header = "Panel de Administración"
admin.site.index_title = "Panel"
admin.site.site_title = "FoodFusion"


admin.site.register(CategoriaMenu)
admin.site.register(Menu)
admin.site.register(Cliente)
admin.site.register(Mesa)
admin.site.register(Reserva)
admin.site.register(Empleado)
admin.site.register(Pedido)
admin.site.register(DetallePedido)