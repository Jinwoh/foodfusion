from django.db import models # type: ignore
from django.contrib.auth.models import User  # type: ignore

# Create your models here.
class CategoriaMenu(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Menu(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(CategoriaMenu, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nombre} - {self.precio} Gs"

class Cliente(models.Model):
   # user = models.Field(User, on_delete=models.CASCADE)
    nombre_apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre_apellido} ({self.cedula})"

class Mesa(models.Model):
    numero = models.PositiveBigIntegerField(unique=True, null=True, blank=True)
    capacidad = models.PositiveIntegerField()
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('reservada', 'Reservada'),
        ('ocupada', 'Ocupada'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='disponible')

    def __str__(self):
        return f"Mesa #{self.id} - {self.estado}"

class Reserva(models.Model):
    fecha_reserva = models.DateTimeField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reserva de {self.cliente.nombre_apellido} para {self.fecha_reserva}"

class Empleado(models.Model):
    nombre_apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    celular = models.CharField(max_length=20)
    correo = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre_apellido

# Historial de pedidos para clientes
class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nombre_apellido}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.menu.nombre} x{self.cantidad} (Pedido #{self.pedido.id})"
    





