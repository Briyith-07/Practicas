from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.utils import timezone
from datetime import datetime
from datetime import date
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,  BaseUserManager



# Modelo personalizado de usuario
class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# luego el modelo Usuario
class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    cargo = models.CharField(max_length=20, choices=ROLES, default='empleado')
    telefono = models.CharField(max_length=15, null=True, blank=True)
    departamento = models.CharField(max_length=50, null=True, blank=True)
    ciudad = models.CharField(max_length=50, null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)

    codigo_temporal = models.CharField(max_length=10, null=True, blank=True)
    fecha_codigo = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
   

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'telefono', 'departamento', 'ciudad', 'direccion']

    
    objects = UsuarioManager()

    def __str__(self):
        return f"{self.email} - {self.cargo or 'Sin cargo'}"

# Roles
class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

# Permisos
class Permiso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='permisos')

    def __str__(self):
        return f"{self.nombre} ({self.rol.nombre})"

# Actividades del SG-SST
class Actividad(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateField()
    responsable = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='actividades_responsables')

    def __str__(self):
        return self.titulo

# Seguimiento de actividades
class Seguimiento(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='seguimientos')
    observaciones = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    realizado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='seguimientos_realizados')

    def __str__(self):
        return f"Seguimiento de {self.actividad.titulo} - {self.fecha}"
    
#codigo campaña
class CodigoCampaña(models.Model):
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=100, default="")

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

# Campañas creadas por el admin
class Campaña(models.Model):
    ESTADOS = [
        ('activa', 'Activa'),
        ('pausada', 'Pausada'),
        ('finalizada', 'Finalizada'),
    ]
    
    codigo = models.OneToOneField(CodigoCampaña, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    detalle = models.TextField()
    estado = models.CharField(max_length=10, choices=ESTADOS, blank=False, null=False)
    recurso = models.FileField(upload_to='campañas/', null=True, blank=True)  
    periodicidad = models.CharField(max_length=100)
    multimedia = models.FileField(upload_to='campañas/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    asignada = models.BooleanField(default=False)
    fecha_asignacion = models.DateField(null=True, blank=True)


    def __str__(self):
        return f"Campana {self.codigo.codigo} - {self.estado}"

# Asignación de campañas a empleados
class CampanaAsignada(models.Model):
    campaña = models.ForeignKey(Campaña, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    realizada = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.campaña.codigo} asignada a {self.empleado.username}"

# Encuesta relacionada a campañas
class Encuesta(models.Model):
    campaña = models.ForeignKey(Campaña, on_delete=models.CASCADE, null=True, blank=True)  
    empleado = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    respuestas = models.TextField()
    evidencia = models.FileField(upload_to='encuestas/', blank=True, null=True)
    fecha = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"Encuesta de {self.empleado.username} sobre {self.campaña.codigo}"

# Feedback de campaña
class Feedback(models.Model):
    campaña = models.ForeignKey(Campaña, on_delete=models.CASCADE, null=True, blank=True)
    empleado = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    calificacion = models.IntegerField()
    comentarios = models.TextField(blank=True)

    def __str__(self):
        return f"Feedback de {self.empleado.username} ({self.calificacion}/5)"

class PausaActiva(models.Model):
    TIPO_CHOICES = [
        ('sopa', 'Sopa de Letras'),
        ('crucigrama', 'Crucigrama'),
        ('movimiento', 'Movimiento Articular'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cargo = models.CharField(max_length=100, help_text="Cargo del participante")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo}) - {self.cargo}"


class SopaLetras(models.Model):
    pausa = models.ForeignKey(PausaActiva, on_delete=models.CASCADE, null=True, blank=True, related_name='sopas')
    titulo = models.CharField(max_length=100)
    instrucciones = models.TextField()
    palabras = models.TextField(help_text="Palabras separadas por comas (,)")

    def __str__(self):
        return f"Sopa: {self.titulo}"

class TemaSopaLetras(models.Model):
    nombre = models.CharField(max_length=100)

class PalabraTema(models.Model):
    tema = models.ForeignKey(TemaSopaLetras, on_delete=models.CASCADE, related_name='palabras')
    texto = models.CharField(max_length=50)

class TemaCrucigrama(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class DefinicionTema(models.Model):
    tema = models.ForeignKey(TemaCrucigrama, on_delete=models.CASCADE, related_name='definiciones')
    palabra = models.CharField(max_length=100)
    definicion = models.TextField()

    def __str__(self):
        return f"{self.palabra}: {self.definicion[:30]}..."
    
class Crucigrama(models.Model):
    pausa = models.ForeignKey(PausaActiva, on_delete=models.CASCADE, null=True, blank=True, related_name='crucigramas')
    titulo = models.CharField(max_length=100)
    instrucciones = models.TextField()
    definiciones = models.TextField(help_text="Separar cada definición con punto y coma (;)")    
    palabras = models.TextField(help_text="Palabras clave separadas por comas (,)")

    def __str__(self):
        return f"Crucigrama: {self.titulo}"


class MovimientoArticular(models.Model):
    pausa = models.ForeignKey(PausaActiva, on_delete=models.CASCADE, null=True, blank=True, related_name='movimientos')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    orden = models.PositiveIntegerField(help_text="Orden en que se debe realizar el ejercicio")
    video_url = models.URLField(blank=True, null=True, help_text="Enlace a un video (opcional)")
    imagen = models.ImageField(upload_to='movimientos/', blank=True, null=True)

    def __str__(self):
        return f"Movimiento: {self.nombre} (Orden: {self.orden})"


class RegistroPausa(models.Model):
    empleado = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    pausa = models.ForeignKey(PausaActiva, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    observacion = models.TextField(blank=True, null=True)
    evidencia = models.FileField(upload_to='evidencias_pausas/', null=True, blank=True)

    def duracion(self):
        """Devuelve duración en minutos"""
        if self.hora_inicio and self.hora_fin:
            delta = datetime.combine(date.min, self.hora_fin) - datetime.combine(date.min, self.hora_inicio)
            return delta.total_seconds() / 60
        return 0

    def __str__(self):
        return f"{self.empleado.email} - {self.pausa.nombre} ({self.fecha})"

class Calificacion(models.Model):
    campaña = models.ForeignKey(Campaña, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    estrellas = models.PositiveIntegerField(default=0)
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.empleado.email} calificó {self.campaña.codigo.codigo} con {self.estrellas} estrellas"

class EvidenciaCampaña(models.Model):
    campaña = models.ForeignKey(Campaña, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='evidencias_campañas/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidencia de {self.empleado.email} - {self.campaña.codigo.codigo}"


