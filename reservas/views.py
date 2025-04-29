from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
# Create your views here.
from .models import *
import traceback

def home(request):
    return render(request, 'home.html')

def registro(request):
    if request.method == 'POST':
        nombre_apellido = request.POST.get('nombre_apellido')
        cedula = request.POST.get('cedula')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password1')

        # Validación básica
        if not all([nombre_apellido, cedula, email, telefono, password]):
            return render(request, 'signup.html', {'error': 'Todos los campos son obligatorios.'})

        # Validar si ya existe usuario
        if User.objects.filter(username=email).exists():
            return render(request, 'signup.html', {'error': 'Ya existe un usuario con ese correo.'})

        # Validar si ya existe cliente con ese correo o cédula
        if Cliente.objects.filter(correo=email).exists() or Cliente.objects.filter(cedula=cedula).exists():
            return render(request, 'signup.html', {'error': 'Cliente ya registrado con ese correo o cédula.'})

        try:
            # Crear usuario
            user = User.objects.create_user(username=email, email=email, password=password)
            user.save()

            # Crear cliente
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
            return redirect('home')

        except IntegrityError as e:
            print("IntegrityError:", e)
            traceback.print_exc()
            return render(request, 'signup.html', {'error': 'Error al registrar. Intente nuevamente.'})

    return render(request, 'signup.html')


# Vista para manejar el inicio de sesión
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)  # Asegúrate de usar 'username' en lugar de 'correo'
        if user is not None:
            auth_login(request, user)  # Usa auth_login para iniciar la sesión
            return redirect('home')  # Redirige a la página principal
        else:
            return render(request, 'login.html', {'error': 'Usuario o Contraseña incorrecta!'}) 
    return render(request, 'login.html')

def menus(request):
    menus = Menu.objects.all()
    return render(request, 'menus.html', {'menus': menus})

@login_required
def signout(request):  # <-- Usamos un nombre diferente
    logout(request)    # <-- Esta vez sí llama a la función real de Django
    return redirect('home')

@login_required
def mis_datos(request):
    datos = Cliente.objects.filter(user=request.user)
    return render(request, 'mis_datos.html', {'mis_datos': datos})





@login_required
def mesas_disponibles(request):
    fecha_str = request.GET.get('fecha')  # formato: YYYY-MM-DD
    hora_str = request.GET.get('hora')    # formato: HH:MM
    duracion_horas = int(request.GET.get('duracion', 2))  # duración por defecto: 2h

    if not fecha_str or not hora_str:
        return render(request, 'mesas_disponibles.html', {'error': 'Debes ingresar fecha y hora.'})

    try:
        fecha_hora_inicio = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        fecha_hora_fin = fecha_hora_inicio + timedelta(hours=duracion_horas)

        # Buscar mesas que NO estén reservadas en el rango solicitado
        reservas_superpuestas = Reserva.objects.filter(
            fecha_reserva__range=(fecha_hora_inicio, fecha_hora_fin)
        ).values_list('mesa_id', flat=True)

        mesas = Mesa.objects.exclude(id__in=reservas_superpuestas)

        return render(request, 'mesas_disponibles.html', {
            'mesas': mesas,
            'fecha': fecha_str,
            'hora': hora_str,
            'duracion': duracion_horas,
        })

    except ValueError:
        return render(request, 'mesas_disponibles.html', {'error': 'Formato de fecha u hora inválido'})
    
@login_required
def reservar_mesa(request, mesa_id):
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        duracion = int(request.POST.get('duracion', 2))

        fecha_hora_inicio = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        fecha_hora_fin = fecha_hora_inicio + timedelta(hours=duracion)

        # Verifica si la mesa está libre en ese rango
        reservas_superpuestas = Reserva.objects.filter(
            mesa_id=mesa_id,
            fecha_reserva__range=(fecha_hora_inicio, fecha_hora_fin)
        )
        if reservas_superpuestas.exists():
            return render(request, 'reserva_error.html', {'error': 'La mesa ya está reservada en ese horario.'})

        try:
            cliente = Cliente.objects.get(correo=request.user.email)

            reservar = Reserva.objects.create(
                fecha_reserva=fecha_hora_inicio,
                cliente=cliente,
                mesa_id=mesa_id
            )
            return redirect('home')  # O a una página de confirmación

        except Cliente.DoesNotExist:
            return render(request, 'reserva_error.html', {'error': 'No se encontró el cliente.'})

