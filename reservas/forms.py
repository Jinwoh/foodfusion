from django import forms
from .models import MensajeNotificacion, Cliente
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client

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
                'fecha': '2025-06-22',
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

            # Enviar WhatsApp
            try:
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                client.messages.create(
                    body=mensaje,
                    from_=settings.TWILIO_WHATSAPP_FROM,
                    to=f"whatsapp:{cliente.telefono}"
                )
            except Exception as e:
                print("Error enviando WhatsApp de prueba:", e)

        # Si es solo prueba, no guardar en DB
        if solo_prueba:
            raise forms.ValidationError("Mensaje de prueba enviado correctamente. No se guardó el mensaje.")

        return super().save(commit)
