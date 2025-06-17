from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import *

class EmpleadoAdmin(UserAdmin):
    model = Empleado
    list_display = ('correo', 'nombre_apellido', 'rol', 'is_staff', 'is_active')
    list_filter = ('rol', 'is_staff')
    fieldsets = (
        (None, {'fields': ('correo', 'password')}),
        ('Información personal', {'fields': ('nombre_apellido', 'cedula', 'celular', 'rol')}),
        ('Permisos', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo', 'nombre_apellido', 'cedula', 'celular', 'rol', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('correo',)
    ordering = ('correo',)

admin.site.register(Empleado, EmpleadoAdmin)
admin.site.register(Rol)

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

admin.site.register(CategoriaMenu, MenuCategoriaAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Mesa)
admin.site.register(Reserva, ReservaAdmin)

@admin.register(ReservaHistorial)
class ReservaHistorialAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'mesa', 'fecha_inicio', 'fecha_fin', 'creada_en', 'eliminado_en')
    list_filter = ('mesa', 'fecha_inicio')
    search_fields = ('cliente__nombre_apellido', 'mesa__numero')
    actions = ['delete_selected']  # Mostrar solo la acción de eliminar

    def get_actions(self, request):
        actions = super().get_actions(request)
        return {'delete_selected': actions['delete_selected']}  # Solo permitir eliminar

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True
