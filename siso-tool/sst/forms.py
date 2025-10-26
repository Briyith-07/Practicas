from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Campaña, Encuesta, Feedback, CodigoCampaña, CampanaAsignada  
from .models import Grupo
from .models import Notificacion
from .models import Usuario, Perfil, EvidenciaCampaña




Usuario = get_user_model()

# Ciudades organizadas por departamento
CIUDADES_POR_DEPARTAMENTO = {
    'Cundinamarca': ['Girardot', 'Soacha', 'Fusagasugá', 'Zipaquirá', 'Ricaurte'],
    'Antioquia': ['Medellín', 'Envigado', 'Bello', 'Itagüí'],
    'Valle del Cauca': ['Cali', 'Palmira', 'Buenaventura', 'Tuluá'],
    'Bogotá': ['Bogotá'],
}

DEPARTAMENTOS = [('', 'Seleccione un departamento')] + [(dep, dep) for dep in CIUDADES_POR_DEPARTAMENTO.keys()]
TODAS_CIUDADES = [('', 'Seleccione una ciudad')] + [(ciudad, ciudad) for ciudades in CIUDADES_POR_DEPARTAMENTO.values() for ciudad in ciudades]

# -----------------------
# Registro de Usuario
# -----------------------

class RegistroUsuarioForm(UserCreationForm):
    cedula = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Cédula' }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}))
    telefono = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Celular'}))
    departamento = forms.ChoiceField(choices=DEPARTAMENTOS, widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_departamento'}))
    ciudad = forms.ChoiceField(choices=TODAS_CIUDADES, widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_ciudad', 'disabled': 'disabled'}))
    direccion = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña',
        'autocomplete': 'new-password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirmar contraseña',
        'autocomplete': 'new-password'
    }))
    terminos = forms.BooleanField(required=True)

    class Meta:
        model = Usuario
        fields = [
            'cedula', 'first_name', 'last_name', 'telefono',
            'departamento', 'ciudad', 'direccion',
            'email', 'password1', 'password2'
        ]

# -----------------------
# Crear Usuario Admin
# -----------------------

class AdminCrearUsuarioForm(UserCreationForm):
    cedula = forms.CharField(label='Cédula', widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='Nombre', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Apellidos', widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(label='Celular', widget=forms.TextInput(attrs={'class': 'form-control'}))
    departamento = forms.ChoiceField(label='Departamento', choices=DEPARTAMENTOS,
                                     widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_departamento'}))
    ciudad = forms.ChoiceField(label='Ciudad', choices=TODAS_CIUDADES,
                               widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_ciudad'}))
    direccion = forms.CharField(label='Dirección', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Correo', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    cargo = forms.ChoiceField(label='Rol', choices=Usuario.ROLES, widget=forms.Select(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Usuario
        fields = ['cedula', 'first_name', 'last_name', 'telefono', 'departamento',
                  'ciudad', 'direccion', 'email', 'cargo', 'password1', 'password2']

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.username = self.cleaned_data['email']
        usuario.email = self.cleaned_data['email']
        usuario.cedula = self.cleaned_data['cedula']
        usuario.cargo = self.cleaned_data['cargo']

        if commit:
            usuario.save()
            # Crear o actualizar el perfil
            perfil, created = Perfil.objects.get_or_create(user=usuario)
            perfil.telefono = self.cleaned_data['telefono']
            perfil.departamento = self.cleaned_data['departamento']
            perfil.ciudad = self.cleaned_data['ciudad']
            perfil.direccion = self.cleaned_data['direccion']
            perfil.save()

        return usuario
# -----------------------
# Editar Usuario Admin
# -----------------------

class AdminEditarUsuarioForm(forms.ModelForm):
    is_active = forms.BooleanField(label='¿Activo?', required=False)

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'telefono', 'departamento', 'ciudad', 'direccion', 'email', 'cargo', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.Select(choices=DEPARTAMENTOS, attrs={'class': 'form-control', 'id': 'id_departamento'}),
            'ciudad': forms.Select(choices=TODAS_CIUDADES, attrs={'class': 'form-control', 'id': 'id_ciudad'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cargo': forms.Select(attrs={'class': 'form-control'}),
        }

# -----------------------
# Campaña
# -----------------------
class CampañaForm(forms.ModelForm):
    codigo = forms.ModelChoiceField(
        queryset=CodigoCampaña.objects.all(),
        empty_label="Seleccione un código",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="Código"
    )

    empleado = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(cargo='empleado'),
        empty_label="Seleccione un empleado",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label="Asignar a empleado"
    )

    # 👇 Aquí el cambio: ModelChoiceField en lugar de ModelMultipleChoiceField
    grupos = forms.ModelChoiceField(
        queryset=Grupo.objects.all(),
        empty_label="Seleccione un grupo",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label="Asignar a grupo"
    )

    periodicidad = forms.ChoiceField(
        choices=[
            ('', 'Seleccione un periodo'),
            ('Diaria', 'Diaria'),
            ('Semanal', 'Semanal'),
            ('Mensual', 'Mensual'),
            ('Bimestral', 'Bimestral'),
            ('Trimestral', 'Trimestral'),
            ('Semestral', 'Semestral'),
            ('Anual', 'Anual'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Periodicidad'
    )

    horario_inicio = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'},
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
        label="Horario de inicio"
    )

    class Meta:
        model = Campaña
        fields = [
            'codigo', 'detalle', 'estado', 'periodicidad',
            'horario_inicio', 'multimedia', 'empleado', 'grupos',
            'evidencia_requerida',
        ]
        widgets = {
            'detalle': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'multimedia': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'evidencia_requerida': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['codigo'].label_from_instance = lambda obj: f"{obj.codigo} - {obj.nombre}"
        self.fields['empleado'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"
        ESTADOS = [('', 'Seleccione un estado')] + list(self.fields['estado'].choices[1:])
        self.fields['estado'].choices = ESTADOS
# -----------------------
# Campaña Asignada
# -----------------------

class CampanaAsignadaForm(forms.ModelForm):  
    class Meta:
        model = CampanaAsignada  
        fields = ['campaña', 'empleado']
        widgets = {
            'campaña': forms.Select(attrs={'class': 'form-control'}),
            'empleado': forms.Select(attrs={'class': 'form-control'}),
        }

# -----------------------
# Código Campaña
# -----------------------

class CodigoCampañaForm(forms.ModelForm):
    class Meta:
        model = CodigoCampaña
        fields = ['codigo', 'nombre']

# -----------------------
# Encuesta
# -----------------------

class EncuestaForm(forms.ModelForm):
    class Meta:
        model = Encuesta
        fields = ['respuestas', 'evidencia']
        widgets = {
            'respuestas': forms.Textarea(attrs={'class': 'form-control'}),
            'evidencia': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# -----------------------
# Feedback
# -----------------------

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['calificacion', 'comentarios']
        widgets = {
            'calificacion': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comentarios': forms.Textarea(attrs={'class': 'form-control'}),
        }
#grupos
class GrupoForm(forms.ModelForm):
    usuarios = forms.ModelMultipleChoiceField(
        queryset=Usuario.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,  # Usuarios opcional
        label="Asignar usuarios al grupo"
    )

    class Meta:
        model = Grupo
        fields = ['nombre', 'descripcion', 'usuarios']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Validar solo los campos obligatorios
        if not cleaned_data.get('nombre'):
            self.add_error('nombre', 'Este campo es obligatorio.')
        if not cleaned_data.get('descripcion'):
            self.add_error('descripcion', 'Este campo es obligatorio.')
        return cleaned_data
#----------------------------------------------------#
class NotificacionForm(forms.ModelForm):
    campaña = forms.ModelChoiceField(
        queryset=Campaña.objects.all(),
        empty_label="Seleccione una campaña",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_campaña'})
    )
    usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(is_active=True, cargo="empleado"),
        empty_label="Seleccione un usuario",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_usuario'})
)

    class Meta:
        model = Notificacion
        fields = ['campaña', 'usuario', 'cedula', 'titulo', 'mensaje', 'tipo']
        widgets = {
            'cedula': forms.TextInput(attrs={'readonly': 'readonly', 'id': 'id_cedula'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        usuario = getattr(getattr(self, 'instance', None), 'usuario', None)
        if usuario:
            self.fields['cedula'].initial = usuario.cedula

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.usuario:
            instance.cedula = instance.usuario.cedula
        if commit:
            instance.save()
        return instance

class EditarUsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Dejar en blanco para no cambiar'}),
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'departamento', 'ciudad']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class AdminEditarUsuarioForm(forms.ModelForm):
    telefono = forms.CharField(required=False)
    direccion = forms.CharField(required=False)   
    departamento = forms.CharField(required=False)
    ciudad = forms.CharField(required=False)
    cedula = forms.CharField(required=False)      

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'cargo']  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'perfil'):
            self.fields['telefono'].initial = self.instance.perfil.telefono
            self.fields['direccion'].initial = self.instance.perfil.direccion
            self.fields['departamento'].initial = self.instance.perfil.departamento
            self.fields['ciudad'].initial = self.instance.perfil.ciudad
            self.fields['cedula'].initial = self.instance.perfil.cedula

    def save(self, commit=True):
        usuario = super().save(commit)
        perfil, created = Perfil.objects.get_or_create(user=usuario)
        perfil.telefono = self.cleaned_data['telefono']
        perfil.direccion = self.cleaned_data['direccion']
        perfil.departamento = self.cleaned_data['departamento']
        perfil.ciudad = self.cleaned_data['ciudad']
        perfil.cedula = self.cleaned_data['cedula']
        perfil.save()
        return usuario
    
#evidencia campaña
class RegistrarEvidenciaCampañaForm(forms.ModelForm):
    class Meta:
        model = EvidenciaCampaña
        fields = ['archivo']
        widgets = {
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }