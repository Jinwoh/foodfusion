from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cliente, Menu, CategoriaMenu, Mesa, Reserva
from datetime import datetime, time, timedelta
from django.utils import timezone
from django.db import IntegrityError
import hashlib
from functools import wraps
from .models import MensajeNotificacion
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.conf import settings           
from django.views.decorators.http import require_POST

# ----------------------------
# Autenticación manual Cliente
# ----------------------------
@csrf_protect
def login_cliente(request):
    if request.method == 'POST':
        correo = request.POST.get('email')
        password = request.POST.get('password')
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            cliente = Cliente.objects.get(correo=correo, password=hashed_password)
            request.session['cliente_id'] = cliente.id
            return redirect('inicio')
        except Cliente.DoesNotExist:
            return render(request, 'login.html', {'error': 'Correo o contraseña incorrectos'})

    return render(request, 'login.html')

def registro_cliente(request):
    if request.method == 'POST':
        nombre_apellido = request.POST.get('nombre_apellido')
        cedula = request.POST.get('cedula')
        correo = request.POST.get('email')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password1')

        if not all([nombre_apellido, cedula, correo, telefono, password]):
            return render(request, 'signup.html', {'error': 'Todos los campos son obligatorios.'})

        if Cliente.objects.filter(correo=correo).exists() or Cliente.objects.filter(cedula=cedula).exists():
            return render(request, 'signup.html', {'error': 'Cliente ya registrado.'})

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            cliente = Cliente(
                nombre_apellido=nombre_apellido,
                cedula=cedula,
                correo=correo,
                telefono=telefono,
                password=hashed_password
            )
            cliente.save()
            request.session['cliente_id'] = cliente.id
            return redirect('inicio')
        except IntegrityError:
            return render(request, 'signup.html', {'error': 'Error al registrar. Intente nuevamente.'})

    return render(request, 'signup.html')


# ----------------------------
# Decorador cliente_required
# ----------------------------
def cliente_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'cliente_id' not in request.session:
            return redirect('login_cliente')
        return view_func(request, *args, **kwargs)
    return wrapper

# ----------------------------
# Logout cliente
# ----------------------------
def signout_cliente(request):
    request.session.flush()
    return redirect('inicio')

# ----------------------------
# Vista inicio
# ----------------------------
def inicio(request):
    categoria_id = request.GET.get('categoria')
    menus = Menu.objects.filter(disponible=True)

    categoria_actual = None
    if categoria_id:
        try:
            categoria_actual = int(categoria_id)
            menus = menus.filter(categoria_id=categoria_actual)
        except ValueError:
            categoria_actual = None

    categorias = CategoriaMenu.objects.all()
    return render(request, 'inicio.html', {
        'menus': menus,
        'categorias': categorias,
        'categoria_actual': categoria_actual
    })
@cliente_required
def mis_datos(request):
    cliente = get_object_or_404(Cliente, id=request.session.get('cliente_id'))
    if request.method == 'POST':
        if 'editar' in request.POST:
            cliente.nombre_apellido = request.POST.get('nombre_apellido')
            cliente.cedula = request.POST.get('cedula')
            cliente.correo = request.POST.get('correo')
            cliente.telefono = request.POST.get('telefono')
            cliente.save()
            messages.success(request, "Datos actualizados correctamente.")
            return redirect('mis_datos') 
        elif 'eliminar' in request.POST:
            password = request.POST.get('password')
            hashed = hashlib.sha256(password.encode()).hexdigest()
            if cliente.password != hashed:
                return render(request, 'mis_datos.html', {
                'cliente': cliente,
                'error': 'Contraseña incorrecta.'
                })
            cliente.delete()
            request.session.flush()
            return redirect('inicio')
    return render(request, 'mis_datos.html', {'cliente': cliente})    



# ----------------------------
# Ver mesas disponibles
# ----------------------------
@cliente_required
def mesas_disponibles(request):
    fecha_str = request.GET.get('fecha')
    hora_inicio_str = request.GET.get('hora_inicio')
    hora_fin_str = request.GET.get('hora_fin')

    mesas_disponibles = []
    horarios_reservados = []
    error = None

    if fecha_str and hora_inicio_str and hora_fin_str:
        try:
            naive_inicio = datetime.strptime(f"{fecha_str} {hora_inicio_str}", "%Y-%m-%d %H:%M")
            naive_fin = datetime.strptime(f"{fecha_str} {hora_fin_str}", "%Y-%m-%d %H:%M")

            fecha_hora_inicio = timezone.make_aware(naive_inicio)
            fecha_hora_fin = timezone.make_aware(naive_fin)

            hora_min = time(17, 0)
            hora_max = time(22, 0)

            # Validaciones
            if fecha_hora_inicio >= fecha_hora_fin:
                error = "La hora de inicio debe ser menor a la de fin."
            elif not (hora_min <= fecha_hora_inicio.time() < hora_max) or not (hora_min < fecha_hora_fin.time() <= hora_max):
                error = "El horario debe ser entre las 17:00 y 22:00."
            elif (fecha_hora_fin - fecha_hora_inicio) < timedelta(minutes=30):
                error = "La duración mínima de la reserva es de 30 minutos."
            else:
                reservas_conflicto = Reserva.objects.filter(
                    fecha_inicio__lt=fecha_hora_fin,
                    fecha_fin__gt=fecha_hora_inicio
                ).values_list('mesa_id', flat=True)

                mesas_disponibles = Mesa.objects.exclude(id__in=reservas_conflicto)

                # Horarios reservados en esa fecha (sin importar mesa)
                fecha_base = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                dia_inicio = timezone.make_aware(datetime.combine(fecha_base, time.min))
                dia_fin = timezone.make_aware(datetime.combine(fecha_base, time.max))
                horarios_reservados = Reserva.objects.filter(
                    fecha_inicio__gte=dia_inicio,
                    fecha_inicio__lte=dia_fin
                ).select_related('mesa').order_by('fecha_inicio')

        except ValueError:
            error = "Formato de fecha u hora inválido."
    elif fecha_str:
        try:
            dia_inicio = timezone.make_aware(datetime.strptime(fecha_str + " 00:00", "%Y-%m-%d %H:%M"))
            dia_fin = timezone.make_aware(datetime.strptime(fecha_str + " 23:59", "%Y-%m-%d %H:%M"))
            horarios_reservados = Reserva.objects.filter(
                fecha_inicio__gte=dia_inicio,
                fecha_inicio__lte=dia_fin
            ).select_related('mesa').order_by('fecha_inicio')
        except ValueError:
            pass

    return render(request, 'mesas_disponibles.html', {
        'mesas': mesas_disponibles,
        'fecha': fecha_str,
        'hora_inicio': hora_inicio_str,
        'hora_fin': hora_fin_str,
        'horarios_reservados': horarios_reservados,
        'error': error,
         # útil si usás select en vez de Flatpickr
    })

# ----------------------------
# Reservar mesa
# ----------------------------
@cliente_required
def reservar_mesa(request, mesa_id):
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
        hora_inicio_str = request.POST.get('hora_inicio')
        hora_fin_str = request.POST.get('hora_fin')

        try:
            naive_inicio = datetime.strptime(f"{fecha_str} {hora_inicio_str}", "%Y-%m-%d %H:%M")
            naive_fin = datetime.strptime(f"{fecha_str} {hora_fin_str}", "%Y-%m-%d %H:%M")
            fecha_hora_inicio = timezone.make_aware(naive_inicio)
            fecha_hora_fin = timezone.make_aware(naive_fin)

            # ❗️Validación nueva
            if fecha_hora_inicio < timezone.now():
                return _respuesta_reserva(request, success=False, error="No se puede reservar en una fecha u hora pasada.")

            if fecha_hora_inicio >= fecha_hora_fin:
                return _respuesta_reserva(request, success=False, error="Hora de inicio debe ser menor a la de fin.")

            hora_min = time(8, 0)
            hora_max = time(22, 0)
            if not (hora_min <= fecha_hora_inicio.time() < hora_max) or not (hora_min < fecha_hora_fin.time() <= hora_max):
                return _respuesta_reserva(request, success=False, error="Horario fuera de rango permitido.")

            cliente = get_object_or_404(Cliente, id=request.session.get('cliente_id'))
            mesa = get_object_or_404(Mesa, pk=mesa_id)

            conflicto = Reserva.objects.filter(
                mesa_id=mesa_id,
                fecha_inicio__lt=fecha_hora_fin,
                fecha_fin__gt=fecha_hora_inicio
            ).exists()

            if conflicto:
                return _respuesta_reserva(request, success=False, error="La mesa ya está reservada en ese horario.")

            Reserva.objects.create(
                fecha_inicio=fecha_hora_inicio,
                fecha_fin=fecha_hora_fin,
                cliente=cliente,
                mesa=mesa
            )

            # Notificación por email (se mantiene igual)
            mensaje_obj = MensajeNotificacion.objects.last()
            if mensaje_obj:
                asunto = mensaje_obj.asunto
                mensaje = mensaje_obj.cuerpo
                for k, v in {
                    'nombre': cliente.nombre_apellido,
                    'mesa': mesa.numero,
                    'capacidad': mesa.capacidad,
                    'fecha': fecha_str,
                    'hora_inicio': hora_inicio_str,
                    'hora_fin': hora_fin_str
                }.items():
                    mensaje = mensaje.replace(f"{{{{ {k} }}}}", str(v))
            else:
                asunto = "Confirmación de reserva - FoodFusion"
                mensaje = f"Hola {cliente.nombre_apellido}, tu reserva fue realizada con éxito.\nMesa: {mesa.numero} - {mesa.capacidad} personas\nDe {hora_inicio_str} a {hora_fin_str}."

            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[cliente.correo],
                fail_silently=True
            )

            return _respuesta_reserva(request, success=True)

        except Exception as e:
            return _respuesta_reserva(request, success=False, error=f"Error interno: {e}")

    return redirect('mesas_disponibles')


def _respuesta_reserva(request, success, error=None):
    """ Responde con JSON si es AJAX, o redirige si es formulario normal """
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({'success': success, 'error': error})
    else:
        if success:
            messages.success(request, 'Reserva realizada con éxito.')
        else:
            messages.error(request, error or 'Ocurrió un error')
        return redirect('mis_reservas')


# ----------------------------
# Menú y filtro por categoría
# ----------------------------
def menus(request):
    categoria_id = request.GET.get('categoria')

    if categoria_id:
        menus = Menu.objects.filter(categoria_id=categoria_id, disponible=True)
    else:
        menus = Menu.objects.filter(disponible=True)

    categorias = CategoriaMenu.objects.all()

    return render(request, 'inicio.html', {
        'menus': menus,
        'categorias': categorias,
        'categoria_actual': int(categoria_id) if categoria_id else None
    })

# ----------------------------
# Ver reservas del cliente
# ----------------------------
@cliente_required
def mis_reservas(request):
    cliente = get_object_or_404(Cliente, id=request.session.get('cliente_id'))
    reservas = Reserva.objects.filter(cliente=cliente).order_by('-fecha_inicio')
    return render(request, 'mis_reservas.html', {'reservas': reservas})

# ----------------------------
# Cancelar reserva
# ----------------------------
@cliente_required
@require_POST
def cancelar_reserva(request, reserva_id):
    try:
        reserva = Reserva.objects.get(id=reserva_id)
        reserva.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True})
        return redirect('mis_reservas')  # Fallback si no es AJAX
    except Reserva.DoesNotExist:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "error": "Reserva no encontrada."}, status=404)
        return redirect('mis_reservas')



def menus_filtrados_json(request):
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        menus = Menu.objects.filter(categoria_id=categoria_id, disponible=True)
    else:
        menus = Menu.objects.filter(disponible=True)

    data = [
    {
        'nombre': menu.nombre,
        'descripcion': menu.descripcion,  # 👈 Agregado
        'img_url': menu.img_url.url if menu.img_url else '/static/img/default-food.jpg'
    }
    for menu in menus
    ]
    return JsonResponse({'menus': data})