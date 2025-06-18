from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Actividad  # Asegúrate de que este modelo exista

def inicio(request):
    return render(request, 'sst/inicio.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect('lista_actividades')
        else:
            messages.error(request, 'Credenciales incorrectas')
    return render(request, 'sst/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro exitoso. Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'sst/register.html', {'form': form})

@login_required
def lista_actividades(request):
    actividades = Actividad.objects.all()
    return render(request, 'sst/actividades.html', {'actividades': actividades})
