from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CategoriaMenu, Menu, Cliente, Mesa, Reserva, Empleado
admin.site.site_header = "Panel de Administración"
admin.site.index_title = "Panel"
admin.site.site_title = "FoodFusion"

class MenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock')


admin.site.register(CategoriaMenu)
admin.site.register(Menu,MenuAdmin)
admin.site.register(Cliente)
admin.site.register(Mesa)
admin.site.register(Reserva)
admin.site.register(Empleado)


