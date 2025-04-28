from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.contrib import messages 
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

# Create your views here.
from .models import Cliente

def home(request):
    return render(request, 'home.html')


def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cedula = request.POST.get('cedula')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')

        # Validaciones antes de crear el usuario
        if User.objects.filter(username=email).exists():
            return render(request, 'login_logout.html', {'error': 'Ya existe un usuario con ese correo'})

        elif Cliente.objects.filter(correo=email).exists() or Cliente.objects.filter(cedula=cedula).exists():
            return render(request, 'signup.html', {'error': 'Cliente ya registrado con ese correo o cédula'})

        try:
            user = User.objects.create_user(username=email, password=password, email=email)
            user.save()

            cliente = Cliente(
                user=user,
                nombre=nombre,
                cedula=cedula,
                correo=email,
                telefono=telefono
            )
            cliente.save()

            messages.success(request, "Cuenta creada con éxito!")
            login(request, user)
            return redirect('home')

        except IntegrityError:
            return render(request, 'signupt.html', {'error': 'Error al registrar. Intente nuevamente.'})

    return render(request, 'signup.html')

# Vista para manejar el inicio de sesión
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirige a la página principal
        else:
            messages.error(request, "Credenciales inválidas.")
    
    return render(request, 'login_logout.html')

def menus(request):
    return render(request, 'menus.html')



