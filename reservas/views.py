from django.shortcuts import redirect, render

# Create your views here.
from .models import Cliente

def registro_usuario(request):
    if request.method == 'POST':
        nombre_apellido = request.POST['nombre_apellido']
        cedula = request.POST['cedula']
        correo = request.POST['correo']
        telefono = request.POST['telefono']

        # Validación básica
        if Cliente.objects.filter(correo=correo).exists() or Cliente.objects.filter(cedula=cedula).exists():
            return render(request, 'reservas/registro.html', {'error': 'Cliente ya registrado con ese correo o cédula'})

        # Crear cliente y guardar en sesión
        cliente = Cliente.objects.create(
            nombre_apellido=nombre_apellido,
            cedula=cedula,
            correo=correo,
            telefono=telefono
        )
        request.session['cliente_id'] = cliente.id  # Guardar ID en sesión
        return redirect('menus')

    return render(request, 'reservas/registro.html')

def login_usuario(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        cedula = request.POST['cedula']

        try:
            cliente = Cliente.objects.get(correo=correo, cedula=cedula)
            request.session['cliente_id'] = cliente.id
            return redirect('menus')
        except Cliente.DoesNotExist:
            return render(request, 'reservas/login.html', {'error': 'Credenciales incorrectas'})

    return render(request, 'reservas/login.html')

def logout_usuario(request):
    request.session.flush()
    return redirect('home')
