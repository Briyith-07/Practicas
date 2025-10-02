from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings 
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Página de inicio
    path('', views.inicio, name='inicio'),

    # Autenticación
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.logout_view, name='logout'),



    # Actividades generales SG-SST
    path('actividades/', views.lista_actividades, name='lista_actividades'),


    # Admin personalizado (usa 'panel/' en lugar de 'admin/')
    path('panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/campanas/crear/', views.crear_campaña, name='crear_campaña'),
    path('panel/usuarios/', views.administrar_usuarios, name='admin_usuarios'),

    # CRUD de usuarios (ADMIN)
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/crear/', views.crear_usuario_admin, name='crear_usuario'),
   
   # Empleado
    path('usuario/editar/<int:usuario_id>/', views.editar_usuario_empleado, name='editar_usuario_empleado'),

# Admin
    path('panel/usuarios/editar/<int:usuario_id>/', views.editar_usuario_admin, name='editar_usuario_admin'),

    path('usuarios/inhabilitar/<int:usuario_id>/', views.inhabilitar_usuario, name='inhabilitar_usuario'),
    path('usuarios/habilitar/<int:usuario_id>/', views.habilitar_usuario, name='habilitar_usuario'),    

    # Encuestas y Feedback a campañas
    path('campañas/<int:campaña_id>/encuesta/', views.encuesta_campaña, name='encuesta_campana'),
    path('campañas/<int:campaña_id>/feedback/', views.feedback_campaña, name='feedback_campana'),
    
    #CRUD campaña
    path('campañas/', views.listar_campañas, name='listar_campañas'),
    path('campañas/crear/', views.crear_campaña, name='crear_campaña'),
    path('campañas/editar/<int:id>/', views.editar_campaña, name='editar_campaña'),
    path('campañas/eliminar/<int:id>/', views.eliminar_campaña, name='eliminar_campaña'),
    
    
    #codigos
    path('codigos/', views.listar_codigos, name='listar_codigos'),
    path('codigos/crear/', views.crear_codigo, name='crear_codigo'),
    path('codigos/editar/<int:id>/', views.editar_codigo, name='editar_codigo'),
    path('codigos/eliminar/<int:id>/', views.eliminar_codigo, name='eliminar_codigo'),
    
    #exportacion
    path('usuarios/exportar/pdf/', views.exportar_usuarios_pdf, name='exportar_usuarios_pdf'),
    path('usuarios/exportar/excel/', views.exportar_usuarios_excel, name='exportar_usuarios_excel'),
    
    # recuperación de contraseña
    path('recuperar/', views.enviar_codigo, name='enviar_codigo'),
    path('verificar-codigo/', views.verificar_codigo, name='verificar_codigo'),
    path('restablecer/<int:id>/', views.restablecer_contraseña, name='restablecer_contraseña'),
    
    #exportar campañas
    path('campañas/exportar/pdf/', views.exportar_campañas_pdf, name='exportar_campañas_pdf'),
    path('campañas/exportar/excel/', views.exportar_campañas_excel, name='exportar_campañas_excel'),
    
    path('estadisticas/', views.estadisticas_menu, name='estadisticas_menu'),
    path('estadisticas/campañas/', views.estadisticas_campañas, name='estadisticas_campañas'),
    path('estadisticas/campañas/creadas/', views.campañas_creadas, name='campañas_creadas'),
    path('estadisticas/campanias/asignadas/', views.campanias_asignadas, name='campanias_asignadas'),
    path('estadisticas/campañas/realizadas/', views.campañas_realizadas, name='campañas_realizadas'),
    path('estadisticas/campañas/sin-realizar/', views.campañas_sin_realizar, name='campañas_sin_realizar'),
    
    
    #empleados
    path('empleado/dashboard/', views.dashboard_empleado, name='dashboard_empleado'),
    path('empleado/campanas-asignadas/', views.campanas_asignadas, name='campanas_asignadas'),
    path('empleado/realizar-campana/', views.realizar_campana, name='realizar_campana'),
    path('empleado/subir-evidencia/', views.subir_evidencia, name='subir_evidencia'),
    path('empleado/campanas-participadas/', views.campanas_participadas, name='campanas_participadas'),
    path('empleado/feedback/', views.feedback_empleado, name='feedback'),
    
     # Asignación de usuarios a campañas
    path('campañas/asignar/', views.asignar_usuario_campania, name='asignar_usuario_campania'),
    
    # CRUD de grupos
    path('grupos/', views.listar_grupos, name='listar_grupos'),
    path('grupos/crear/', views.crear_grupo, name='crear_grupo'),
    
    # Notificaciones
    path('listar/', views.listar_notificaciones, name='listar_notificaciones'),
    path("crear/", views.crear_notificacion, name="crear_notificacion"),
    path("notificaciones/json/", views.notificaciones_json, name="notificaciones_json"),
    path("notificaciones/leida/<int:pk>/", views.marcar_notificacion_leida, name="marcar_notificacion_leida"),
    path("api/notificaciones/", views.api_notificaciones, name="api_notificaciones"),
    path("editar/<int:pk>/", views.editar_notificacion, name="editar_notificacion"),
    path("eliminar/<int:pk>/", views.eliminar_notificacion, name="eliminar_notificacion"),
    path("detalle-admin/<int:pk>/", views.detalle_notificacion_admin, name="detalle_notificacion_admin"),
    path('pausa/<int:pausa_id>/ejecutar/', views.ejecutar_pausa, name='ejecutar_pausa'),
  
    
    
    #usuario
    path('perfil/modificar/', views.perfil_modificar, name='perfil_modificar'),
   
    #notificaciones empleado
    path("listar/empleado/", views.listar_notificaciones_empleado, name="listar_notificaciones_empleado"),
    path("notificacion/<int:pk>/", views.detalle_notificacion_empleado, name="detalle_notificacion_empleado"),
    
    #grupos
    path('grupos/', views.listar_grupos, name='listar_grupos'),
    path('grupos/crear/', views.crear_grupo, name='crear_grupo'),
    path('grupos/editar/<int:id>/', views.editar_grupo, name='editar_grupo'),
    path('grupos/eliminar/<int:id>/', views.eliminar_grupo, name='eliminar_grupo'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
