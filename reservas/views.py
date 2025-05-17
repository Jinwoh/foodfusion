from multiprocessing import context
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, time
from django.utils import timezone
from .models import Cliente, Empleado, Menu, CategoriaMenu, Mesa, Reserva
import traceback

# --- DECORATORS ---
def cliente_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not Cliente.objects.filter(user=request.user).exists():
            return redirect('clientes:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def empleado_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not Empleado.objects.filter(user=request.user).exists():
            return redirect('empleados:login')
        return view_func(request, *args, **kwargs)
    return wrapper

# --- CLIENTE VIEWS ---
def login_cliente(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user and Cliente.objects.filter(user=user).exists():
            auth_login(request, user)
            return redirect('clientes:home')
        messages.error(request, 'Credenciales inválidas o no eres cliente.')
    return render(request, 'clientes/login.html')


def registro_cliente(request):
    if request.method == 'POST':
        # (igual que antes, creando User y Cliente)
        # ... tu lógica de registro aquí ...
        auth_login(request, user) # type: ignore
        return redirect('clientes:home')
    return render(request, 'clientes/signup.html')

@login_required
@cliente_required
def home_cliente(request):
    # tu lógica de mostrar menús, etc.
    return render(request, 'clientes/inicio.html', context)

# ... resto de views protegidas con @cliente_required ...

# --- EMPLEADO (ADMIN) VIEWS ---
def login_empleado(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user and Empleado.objects.filter(user=user).exists():
            auth_login(request, user)
            return redirect('empleados:panel_home')
        messages.error(request, 'Credenciales inválidas o no eres empleado.')
    return render(request, 'empleados/login.html')

@login_required
@empleado_required
def panel_home(request):
    # lógica del dashboard de administración
    return render(request, 'empleados/panel_home.html')

# Todas las demás vistas de administración deben usar @empleado_required

@login_required
def logout_view(request):
    logout(request)
    return redirect('inicio')

