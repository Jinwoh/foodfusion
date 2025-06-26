from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.conf import settings
from twilio.rest import Client
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect
from .forms import *
from django.urls import path


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


class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero_display', 'capacidad_display', 'estado_display')

    def numero_display(self, obj):
        return obj.numero
    numero_display.short_description = 'Número de Mesa'

    def capacidad_display(self, obj):
        return obj.capacidad
    capacidad_display.short_description = 'Capacidad de Personas'

    def estado_display(self, obj):
        return obj.estado
    estado_display.short_description = 'Estado actual'

admin.site.register(CategoriaMenu, MenuCategoriaAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Mesa, MesaAdmin)
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
    

class MensajeNotificacionForm(forms.ModelForm):
    cliente_prueba = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        required=False,
        label="Enviar prueba a"
    )
    enviar_prueba = forms.BooleanField(
        required=False,
        label="Enviar solo prueba (no guardar mensaje)"
    )

    class Meta:
        model = MensajeNotificacion
        fields = ['asunto', 'cuerpo', 'cliente_prueba', 'enviar_prueba']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('enviar_prueba') and not cleaned_data.get('cliente_prueba'):
            raise forms.ValidationError("Debes seleccionar un cliente para enviar una prueba.")
        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        cliente = cleaned_data.get('cliente_prueba')
        solo_prueba = cleaned_data.get('enviar_prueba')

        # Reemplazo del mensaje
        if cliente:
            mensaje = cleaned_data['cuerpo']
            asunto = cleaned_data['asunto']
            datos = {
                'nombre': cliente.nombre_apellido,
                'mesa': '12',
                'capacidad': '4',
                'fecha': '2025-06-20',
                'hora_inicio': '19:00',
                'hora_fin': '20:00'
            }
            for clave, valor in datos.items():
                mensaje = mensaje.replace(f"{{{{ {clave} }}}}", valor)

            # Enviar correo
            try:
                send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [cliente.correo])
            except Exception as e:
                print("Error enviando correo de prueba:", e)

        return super().save(commit)


@admin.register(MensajeNotificacion)
class MensajeNotificacionAdmin(admin.ModelAdmin):
    form = MensajeNotificacionForm
    list_display = ['asunto', 'fecha_creacion']
    readonly_fields = ['fecha_creacion']

    def save_model(self, request, obj, form, change):
        # Solo guardar si no es prueba
        if not form.cleaned_data.get('enviar_prueba', False):
            super().save_model(request, obj, form, change)
