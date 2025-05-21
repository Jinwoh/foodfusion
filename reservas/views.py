from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cliente, Menu, CategoriaMenu, Mesa, Reserva
from datetime import datetime, timedelta, time
from django.utils import timezone
from django.db import IntegrityError
import hashlib
from functools import wraps

# ----------------------------
# Autenticación manual Cliente
# ----------------------------
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
            return redirect('login')
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

# ----------------------------
# Editar datos del cliente
# ----------------------------
@cliente_required
def editar_datos(request):
    cliente = get_object_or_404(Cliente, id=request.session.get('cliente_id'))
    if request.method == 'POST':
        cliente.nombre_apellido = request.POST.get('nombre_apellido')
        cliente.cedula = request.POST.get('cedula')
        cliente.correo = request.POST.get('correo')
        cliente.telefono = request.POST.get('telefono')
        cliente.save()
        return redirect('mis_datos')
    return render(request, 'editar_datos.html', {'cliente': cliente})

# ----------------------------
# Eliminar cuenta del cliente
# ----------------------------
@cliente_required
def eliminar_cuenta(request):
    cliente = get_object_or_404(Cliente, id=request.session.get('cliente_id'))
    if request.method == 'POST':
        password = request.POST.get('password')
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if cliente.password != hashed:
            return render(request, 'mis_datos.html', {'error': 'Contraseña incorrecta.'})

        cliente.delete()
        request.session.flush()
        return redirect('inicio')

    return render(request, 'mis_datos.html')

# ----------------------------
# Ver datos del cliente
# ----------------------------
@cliente_required
def mis_datos(request):
    cliente = get_object_or_404(Cliente, id=request.session.get('cliente_id'))
    return render(request, 'mis_datos.html', {'mis_datos': [cliente]})

# ----------------------------
# Ver mesas disponibles
# ----------------------------
def mesas_disponibles(request):
    fecha_str = request.GET.get('fecha')
    hora_str = request.GET.get('hora')
    duracion_horas = int(request.GET.get('duracion', 2))

    if not fecha_str or not hora_str:
        return render(request, 'mesas_disponibles.html', {'error': 'Debes ingresar la fecha y la hora para buscar mesas.'})

    try:
        naive_inicio = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        fecha_hora_inicio = timezone.make_aware(naive_inicio)
        fecha_hora_fin = fecha_hora_inicio + timedelta(hours=duracion_horas)

        hora_min = time(8, 0)
        hora_max = time(22, 0)

        if not (hora_min <= fecha_hora_inicio.time() < hora_max):
            return render(request, 'mesas_disponibles.html', {'error': 'El horario de reserva debe ser entre las 08:00 y las 22:00.'})
        if fecha_hora_fin.time() > hora_max:
            return render(request, 'mesas_disponibles.html', {'error': 'La duración excede el horario máximo permitido (22:00).'})

        reservas_conflicto = Reserva.objects.filter(
            fecha_inicio__lt=fecha_hora_fin,
            fecha_fin__gt=fecha_hora_inicio
        ).values_list('mesa_id', flat=True)

        mesas_disponibles = Mesa.objects.exclude(id__in=reservas_conflicto)

        return render(request, 'mesas_disponibles.html', {
            'mesas': mesas_disponibles,
            'fecha': fecha_str,
            'hora': hora_str,
            'duracion': duracion_horas,
        })

    except ValueError:
        return render(request, 'mesas_disponibles.html', {'error': 'Formato de fecha u hora inválido.'})

# ----------------------------
# Reservar mesa
# ----------------------------
@cliente_required
def reservar_mesa(request, mesa_id):
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        duracion = int(request.POST.get('duracion', 2))

        try:
            naive_inicio = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
            fecha_hora_inicio = timezone.make_aware(naive_inicio)
            fecha_hora_fin = fecha_hora_inicio + timedelta(hours=duracion)

            reservas_conflicto = Reserva.objects.filter(
                mesa_id=mesa_id,
                fecha_inicio__lt=fecha_hora_fin,
                fecha_fin__gt=fecha_hora_inicio
            )
            if reservas_conflicto.exists():
                return render(request, 'reserva_error.html', {'error': 'La mesa ya está reservada en ese horario.'})

            cliente = get_object_or_404(Cliente, id=request.session.get('cliente_id'))
            mesa = get_object_or_404(Mesa, pk=mesa_id)

            Reserva.objects.create(
                fecha_inicio=fecha_hora_inicio,
                fecha_fin=fecha_hora_fin,
                cliente=cliente,
                mesa=mesa
            )

            messages.success(request, 'Reserva realizada con éxito.')
            return redirect('mis_reservas')

        except Exception:
            return render(request, 'reserva_error.html', {'error': 'Error al procesar la reserva.'})

    return redirect('mesas_disponibles')

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
def cancelar_reserva(request, reserva_id):
    cliente = get_object_or_404(Cliente, id=request.session.get('cliente_id'))
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=cliente)
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, 'La reserva ha sido cancelada exitosamente.')
        return redirect('mis_reservas')
    return redirect('mis_reservas')
