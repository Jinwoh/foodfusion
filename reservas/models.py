from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# --- Roles y Empleados (Sistema de autenticación personalizado) ---
class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class EmpleadoManager(BaseUserManager):
    def create_user(self, correo, nombre_apellido, cedula, celular, password=None):
        if not correo:
            raise ValueError('El usuario debe tener un correo')
        user = self.model(
            correo=correo,
            nombre_apellido=nombre_apellido,
            cedula=cedula,
            celular=celular
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, nombre_apellido, cedula, celular, password):
        user = self.create_user(
            correo=correo,
            nombre_apellido=nombre_apellido,
            cedula=cedula,
            celular=celular,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Empleado(AbstractBaseUser, PermissionsMixin):
    correo = models.EmailField(unique=True)
    nombre_apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    celular = models.CharField(max_length=20)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = EmpleadoManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre_apellido', 'cedula', 'celular']

    def __str__(self):
        return self.nombre_apellido

# --- Modelos del sistema ---
class CategoriaMenu(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Menu(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey('CategoriaMenu', on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField()
    disponible = models.BooleanField(default=True)
    img_url = models.ImageField(upload_to='menus/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.precio} Gs"

class Cliente(models.Model):
    nombre_apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    password = models.CharField(max_length=128)

    NOTIFICACION_CHOICES = [
        ('email', 'Correo'),
        ('whatsapp', 'WhatsApp'),
        ('ambos', 'Ambos'),
    ]
    preferencia_notificacion = models.CharField(
        max_length=10,
        choices=NOTIFICACION_CHOICES,
        default='email'
    )

    def __str__(self):
        return self.nombre_apellido

class Mesa(models.Model):
    numero = models.PositiveBigIntegerField(unique=True, null=True, blank=True)
    capacidad = models.PositiveIntegerField()
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('reservada', 'Reservada'),
        ('ocupada', 'Ocupada'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)

    def __str__(self):
        return f"Mesa #{self.numero or self.id} - {self.estado}"

class Reserva(models.Model):
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)  

    def __str__(self):
        return f"Reserva de {self.cliente.nombre_apellido} desde {self.fecha_inicio} hasta {self.fecha_fin}"
    
class ReservaHistorial(models.Model):
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    cliente = models.ForeignKey('Cliente', on_delete=models.DO_NOTHING)
    mesa = models.ForeignKey('Mesa', on_delete=models.DO_NOTHING)
    eliminado_en = models.DateTimeField()
    creada_en = models.DateTimeField(null=True)  # nueva columna

    class Meta:
        managed = False
        db_table = 'reserva_historial'

    def __str__(self):
        return f"{self.cliente} - Mesa {self.mesa} - {self.fecha_inicio} → {self.fecha_fin}"
