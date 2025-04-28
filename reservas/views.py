from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
# Create your views here.
from .models import *

def home(request):
    return render(request, 'home.html')


def registro(request):
    if request.method == 'POST':
        nombre_apellido = request.POST.get('nombre_apellido')  # Corregir campo 'username' a 'nombre_apellido'
        cedula = request.POST.get('cedula')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password1')  # Corregir el nombre del campo a 'password1'

        # Validaciones antes de crear el usuario
        if User.objects.filter(email=email).exists():  # Cambiar 'correo' a 'email'
            return render(request, 'signup.html', {'error': 'Ya existe un usuario con ese correo'})

        elif Cliente.objects.filter(correo=email).exists() or Cliente.objects.filter(cedula=cedula).exists():
            return render(request, 'signup.html', {'error': 'Cliente ya registrado con ese correo o cédula'})

        try:
            # Crear usuario con 'username' como email, que es lo que normalmente se usa para el login
            user = User.objects.create_user(username=email, email=email, password=password)
            user.save()

            cliente = Cliente(
                
                nombre_apellido=nombre_apellido,
                cedula=cedula,
                correo=email,  # Asegúrate de usar 'correo' aquí
                telefono=telefono
            )
            cliente.save()

            messages.success(request, "Cuenta creada con éxito!")
            auth_login(request, user)  # Usar 'auth_login' en lugar de 'login'
            return redirect('home')

        except IntegrityError:
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
            messages.error(request, "Credenciales inválidas.")
    
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
    mis_datos = Cliente.objects.all()
    return render(request, 'mis_datos.html', {'mis_datos': mis_datos})