from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.conf import settings






# =========================
#   USUARIOS Y ROLES
# =========================
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


class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
    )

    cedula = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    cargo = models.CharField(max_length=20, choices=ROLES, default='empleado')
    telefono = models.CharField(max_length=15)
    departamento = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255)

    codigo_temporal = models.CharField(max_length=10, null=True, blank=True)
    fecha_codigo = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['cedula', 'first_name', 'last_name', 'telefono', 'departamento', 'ciudad', 'direccion']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='permisos')

    def __str__(self):
        return f"{self.nombre} ({self.rol.nombre})"


# =========================
#   GRUPOS
# =========================
class Grupo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    usuarios = models.ManyToManyField("Usuario", related_name="grupos", blank=True)

    def __str__(self):
        return self.nombre


# =========================
#   ACTIVIDADES SG-SST
# =========================
class Actividad(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateField()
    responsable = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='actividades_responsables')

    def __str__(self):
        return self.titulo


class Seguimiento(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='seguimientos')
    observaciones = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    realizado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='seguimientos_realizados')

    def __str__(self):
        return f"Seguimiento de {self.actividad.titulo} - {self.fecha}"


# =========================
#   CAMPAÑAS (PAUSAS ACTIVAS)
# =========================
class CodigoCampaña(models.Model):
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=100, default="")

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Campaña(models.Model):
    ESTADOS = [
        ('activa', 'Activa'),              # Cuando se asigna la campaña
        ('pausada', 'Pausada'),            # Cuando el usuario la ve pero no la ejecuta
        ('por_aprobacion', 'Por aprobación'),  # Cuando sube la evidencia
        ('finalizada', 'Finalizada'),      # Cuando el admin aprueba la evidencia
    ]

    PERIODICIDADES = [
        ('Diaria', 'Diaria'),
        ('Semanal', 'Semanal'),
        ('Mensual', 'Mensual'),
        ('Bimestral', 'Bimestral'),
        ('Trimestral', 'Trimestral'),
        ('Semestral', 'Semestral'),
        ('Anual', 'Anual'),
    ]

    codigo = models.OneToOneField(CodigoCampaña, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    detalle = models.TextField()
    estado = models.CharField(
    max_length=20,
    choices=ESTADOS,
    default='activa',  # por defecto activa al asignarse
    blank=True,         # ✅ ya no será obligatorio en formularios
    null=True,          # ✅ permite valores nulos si no se pasa nada
    verbose_name="Estado actual"
)

    actividad = models.ForeignKey("Actividad", on_delete=models.SET_NULL, null=True, blank=True)
    recurso = models.FileField(upload_to='campañas/', null=True, blank=True)
    multimedia = models.FileField(upload_to='campañas/', blank=True, null=True)

    periodicidad = models.CharField(
        max_length=20,
        choices=PERIODICIDADES,
        blank=True,
        null=True,
        verbose_name="Periodicidad"
    )

    horario_inicio = models.TimeField(blank=True, null=True, help_text="Hora de inicio de la pausa")
    evidencia_requerida = models.BooleanField(default=False)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    usuarios = models.ManyToManyField("Usuario", through="CampanaAsignada", blank=True)
    grupos = models.ManyToManyField("Grupo", related_name="campañas", blank=True)

    def __str__(self):
        return f"{self.codigo.codigo} - {self.nombre or ''}"

    # ==============================
    #   MÉTODOS DE CAMBIO DE ESTADO
    # ==============================
    def marcar_pausada(self):
        """Cuando el usuario ve la campaña pero no ejecuta ni sube evidencia."""
        if self.estado == "activa":
            self.estado = "pausada"
            self.save()

    def marcar_por_aprobacion(self):
        """Cuando el usuario sube la evidencia."""
        if self.estado in ["activa", "pausada"]:
            self.estado = "por_aprobacion"
            self.save()

    def marcar_finalizada(self):
        """Cuando el admin aprueba la evidencia."""
        if self.estado == "por_aprobacion":
            self.estado = "finalizada"
            self.save()


class CampanaAsignada(models.Model):
    campaña = models.ForeignKey(Campaña, on_delete=models.CASCADE)
    empleado = models.ForeignKey("Usuario", on_delete=models.CASCADE, null=True, blank=True)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    realizada = models.BooleanField(default=False)

    @property
    def campana(self):
        return self.campaña

    def __str__(self):
        return f"{self.campaña.nombre} asignada a {self.empleado.email}"


# =========================
#   NOTIFICACIONES
# =========================

#pausas activas

class PausaActiva(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20)
    duracion = models.PositiveIntegerField()

    def __str__(self):
        return self.nombre
    
    
class Notificacion(models.Model):
    TIPOS = [
        ('correo', 'Correo Electrónico'),
        ('web', 'Notificación Web'),
    ]   

    campaña = models.ForeignKey("Campaña", on_delete=models.CASCADE)
    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    cedula = models.CharField(max_length=20, blank=True, null=True)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPOS, default='web')
    enviada = models.BooleanField(default=False)
    abierta = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_apertura = models.DateTimeField(null=True, blank=True)
    pausa = models.ForeignKey(PausaActiva, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        if self.usuario:
            return f"Notificación {self.titulo} a {self.usuario.email}"
        return f"Notificación {self.titulo} (sin usuario)"
    


# =========================
#   REGISTRO DE CAMPAÑAS REALIZADAS
# =========================
class CampañaRealizada(models.Model):
    campaña = models.ForeignKey(Campaña, on_delete=models.CASCADE)
    empleado = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    cedula = models.CharField(max_length=20)
    evidencia = models.FileField(upload_to="evidencias_campañas/", blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.empleado.email} completó {self.campaña.nombre}"


# =========================
#   ENCUESTAS Y FEEDBACK
# =========================
class Encuesta(models.Model):
    campaña = models.ForeignKey(Campaña, on_delete=models.CASCADE, null=True, blank=True)  
    empleado = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    respuestas = models.TextField()
    evidencia = models.FileField(upload_to='encuestas/', blank=True, null=True)
    fecha = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"Encuesta de {self.empleado.email} sobre {self.campaña.codigo}"


class Feedback(models.Model):
    campaña = models.ForeignKey(Campaña, on_delete=models.CASCADE, null=True, blank=True)
    empleado = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    calificacion = models.IntegerField()
    comentarios = models.TextField(blank=True)

    def __str__(self):
        return f"Feedback de {self.empleado.email} ({self.calificacion}/5)"


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
    
class Perfil(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.email
