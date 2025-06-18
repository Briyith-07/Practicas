from django.db import models
from django.contrib.auth.models import AbstractUser

# Usuario personalizado
class Usuario(AbstractUser):
    cargo = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.cargo or 'Sin cargo'}"

# Rol del sistema (Ej: Coordinador, Auxiliar, Inspector)
class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

# Permisos asociados a roles
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
