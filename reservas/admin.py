from django.contrib import admin
from django.utils.html import format_html
# Register your models here.
from django.contrib import admin
from .models import CategoriaMenu, Menu, Cliente, Mesa, Reserva, Empleado
admin.site.site_header = "Panel de Administración"
admin.site.index_title = "Panel"
admin.site.site_title = "FoodFusion"

class MenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'preview_img')

    def preview_img(self, obj):
        if obj.img_url:
            return format_html('<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 5px;" />', obj.img_url.url)
        return "Sin imagen"

    preview_img.short_description = "Imagen"

class ReservaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'mesa', 'fecha_inicio', 'fecha_fin')

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_apellido', 'cedula', 'correo', 'telefono')

class MenuCategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

admin.site.register(CategoriaMenu,MenuCategoriaAdmin)
admin.site.register(Menu,MenuAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Mesa)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(Empleado)


