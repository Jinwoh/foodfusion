from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, time
from django.utils import timezone
from .models import *
import traceback

def cliente_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not Cliente.objects.filter(user=request.user).exists():
            logout(request)
            return redirect('inicio')
        return view_func(request, *args, **kwargs)
    return wrapper

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

def registro(request):
    if request.method == 'POST':
        nombre_apellido = request.POST.get('nombre_apellido')
        cedula = request.POST.get('cedula')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password1')

        if not all([nombre_apellido, cedula, email, telefono, password]):
            return render(request, 'signup.html', {'error': 'Todos los campos son obligatorios.'})

        if User.objects.filter(username=email).exists():
            return render(request, 'signup.html', {'error': 'Ya existe un usuario con ese correo.'})

        if Cliente.objects.filter(correo=email).exists() or Cliente.objects.filter(cedula=cedula).exists():
            return render(request, 'signup.html', {'error': 'Cliente ya registrado con ese correo o cédula.'})

        try:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.save()

            cliente = Cliente(
                user=user,
                nombre_apellido=nombre_apellido,
                cedula=cedula,
                correo=email,
                telefono=telefono
            )
            cliente.save()

            messages.success(request, "Cuenta creada con éxito.")
            auth_login(request, user)
            return redirect('inicio')

        except IntegrityError as e:
            traceback.print_exc()
            return render(request, 'signup.html', {'error': 'Error al registrar. Intente nuevamente.'})

    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('inicio')
        else:
            return render(request, 'login.html', {'error': 'Usuario o Contraseña incorrecta!'})
    return render(request, 'login.html')

@login_required
@cliente_required
def editar_datos(request):
    cliente = Cliente.objects.get(user=request.user)
    if request.method == 'POST':
        cliente.nombre_apellido = request.POST.get('nombre_apellido')
        cliente.cedula = request.POST.get('cedula')
        cliente.correo = request.POST.get('correo')
        cliente.telefono = request.POST.get('telefono')
        cliente.save()
        return redirect('mis_datos')
    return render(request, 'editar_datos.html', {'cliente': cliente})

@login_required
@cliente_required
def eliminar_cuenta(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.user
        if not user.check_password(password):
            return render(request, 'mis_datos.html', {'error': 'Contraseña incorrecta.'})

        try:
            cliente = Cliente.objects.get(user=user)
            cliente.delete()
            user.delete()
            logout(request)
            return redirect('inicio')
        except Cliente.DoesNotExist:
            messages.error(request, 'No se encontró el cliente asociado a esta cuenta.')
            return redirect('mis_datos')

    return render(request, 'mis_datos.html')

@login_required
def signout(request):
    logout(request)
    return redirect('inicio')

@login_required
@cliente_required
def mis_datos(request):
    cliente = Cliente.objects.get(user=request.user)
    if request.method == 'POST':
        if 'editar' in request.POST:
            cliente.nombre_apellido = request.POST.get('nombre_apellido')
            cliente.cedula = request.POST.get('cedula')
            cliente.correo = request.POST.get('correo')
            cliente.telefono = request.POST.get('telefono')
            cliente.save()
            return redirect('mis_datos')
    return render(request, 'mis_datos.html', {'mis_datos': [cliente]})

@login_required
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

@login_required
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

            cliente = get_object_or_404(Cliente, user=request.user)
            mesa = get_object_or_404(Mesa, pk=mesa_id)

            Reserva.objects.create(
                fecha_inicio=fecha_hora_inicio,
                fecha_fin=fecha_hora_fin,
                cliente=cliente,
                mesa=mesa
            )

            messages.success(request, 'Reserva realizada con éxito.')
            return redirect('mis_reservas')

        except Exception as e:
            return render(request, 'reserva_error.html', {'error': 'Error al procesar la reserva.'})

    return redirect('mesas_disponibles')

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

@login_required
def mis_reservas(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    reservas = Reserva.objects.filter(cliente=cliente).order_by('-fecha_inicio')
    return render(request, 'mis_reservas.html', {'reservas': reservas})

@login_required
@cliente_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__user=request.user)
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, 'La reserva ha sido cancelada exitosamente.')
        return redirect('mis_reservas')
    return redirect('mis_reservas')
