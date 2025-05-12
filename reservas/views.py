from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .models import *
import traceback
from datetime import datetime, timedelta, time

def cliente_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not Cliente.objects.filter(user=request.user).exists():
            messages.error(request, 'Tu cuenta no está registrada como cliente.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper





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

# Función para editar datos.

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


# Función para eliminar la cuenta.
@login_required
@cliente_required
def eliminar_cuenta(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.user

        # Verifica la contraseña ingresada
        if not user.check_password(password):
            return render(request, 'mis_datos.html', {'error': 'Contraseña incorrecta.'})

        try:
            # Obtener cliente
            cliente = Cliente.objects.get(user=user)
            # Eliminar cliente y usuario
            cliente.delete()
            user.delete()

            # Cerrar sesión
            logout(request)

            # Redirigir a la página de inicio
            return redirect('home')

        except Cliente.DoesNotExist:
            messages.error(request, 'No se encontró el cliente asociado a esta cuenta.')
            return redirect('mis_datos')

    return render(request, 'mis_datos.html')




def menus(request):
    menus = Menu.objects.all()
    return render(request, 'menus.html', {'menus': menus})

@login_required
def signout(request):  # <-- Usamos un nombre diferente
    logout(request)    # <-- Esta vez sí llama a la función real de Django
    return redirect('home')



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

        elif 'eliminar' in request.POST:
            password = request.POST.get('password')
            if not request.user.check_password(password):
                return render(request, 'mis_datos.html', {'mis_datos': [cliente], 'error': 'Contraseña incorrecta.'})
            
            # Usar timezone.now() correctamente


    return render(request, 'mis_datos.html', {'mis_datos': [cliente]})







@login_required
def mesas_disponibles(request):
    fecha_str = request.GET.get('fecha')
    hora_str = request.GET.get('hora')
    duracion_horas = int(request.GET.get('duracion', 2))

    if not fecha_str or not hora_str:
        return render(request, 'mesas_disponibles.html', {
            'error': 'Debes ingresar la fecha y la hora para buscar mesas.'
        })

    try:
        # Combinar fecha y hora
        fecha_hora_inicio = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        fecha_hora_fin = fecha_hora_inicio + timedelta(hours=duracion_horas)

        # Validación de horario permitido
        hora_min = time(8, 0)
        hora_max = time(22, 0)

        if not (hora_min <= fecha_hora_inicio.time() < hora_max):
            return render(request, 'mesas_disponibles.html', {
                'error': 'El horario de reserva debe ser entre las 08:00 y las 22:00.'
            })

        if fecha_hora_fin.time() > hora_max:
            return render(request, 'mesas_disponibles.html', {
                'error': 'La duración excede el horario máximo permitido (22:00).'
            })

        # Buscar IDs de mesas que estén ocupadas en el rango
        reservas_conflicto = Reserva.objects.filter(
            fecha_inicio__lt=fecha_hora_fin,
            fecha_fin__gt=fecha_hora_inicio
        ).values_list('mesa_id', flat=True)

        # Excluir esas mesas
        mesas_disponibles = Mesa.objects.exclude(id__in=reservas_conflicto)

        return render(request, 'mesas_disponibles.html', {
            'mesas': mesas_disponibles,
            'fecha': fecha_str,
            'hora': hora_str,
            'duracion': duracion_horas,
        })

    except ValueError:
        return render(request, 'mesas_disponibles.html', {
            'error': 'Formato de fecha u hora inválido.'
        })
    

@login_required
@cliente_required
def reservar_mesa(request, mesa_id):
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        duracion = int(request.POST.get('duracion', 2))

        try:
            fecha_hora_inicio = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
            fecha_hora_fin = fecha_hora_inicio + timedelta(hours=duracion)

            # Verificar disponibilidad
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
            return redirect('home')  # O redirigir a una página de confirmación

        except Exception as e:
            return render(request, 'reserva_error.html', {'error': 'Error al procesar la reserva.'})

    return redirect('mesas_disponibles')


@login_required
def mis_reservas(request):
    cliente = get_object_or_404(Cliente, user=request.user)

    reservas = Reserva.objects.filter(cliente=cliente).order_by('-fecha_inicio')

    return render(request, 'mis_reservas.html', {
        'reservas': reservas
    })