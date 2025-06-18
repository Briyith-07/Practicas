from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('actividades/', views.lista_actividades, name='lista_actividades'),
]
