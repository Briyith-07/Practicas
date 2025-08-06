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
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/inhabilitar/<int:usuario_id>/', views.inhabilitar_usuario, name='inhabilitar_usuario'),
    path('usuarios/habilitar/<int:usuario_id>/', views.habilitar_usuario, name='habilitar_usuario'),

    # Empleado
    path('empleado/dashboard/', views.dashboard_empleado, name='dashboard_empleado'),
    path('empleado/campanas-asignadas/', views.campañas_asignadas, name='campañas_asignadas'),

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
    path('estadisticas/pausas/', views.estadisticas_pausas, name='estadisticas_pausas'),
    path('estadisticas/campañas/', views.estadisticas_campañas, name='estadisticas_campañas'),
    path('estadisticas/campañas/creadas/', views.campañas_creadas, name='campañas_creadas'),
    path('estadisticas/campanias/asignadas/', views.campanias_asignadas, name='campanias_asignadas'),
    path('estadisticas/campañas/realizadas/', views.campañas_realizadas, name='campañas_realizadas'),
    path('estadisticas/campañas/sin-realizar/', views.campañas_sin_realizar, name='campañas_sin_realizar'),
    
    #pausas
    path('pausas/crear/', views.crear_pausa, name='crear_pausa'),
    path('pausas/registro/', views.registro_pausas, name='registro_pausas'),
    path('pausas/asignacion/', views.asignacion_pausas, name='asignacion_pausas'),
    # Nuevas subrutas de pausas
    path('pausas/crear/', views.crear_pausa, name='crear_pausa'),
    path('pausas/creadas/', views.ver_pausas_creadas, name='ver_pausas_creadas'),
    path('pausas/crear/', views.pausas_crear_menu, name='pausas_crear_menu'),
    path('pausas/listar/', views.listar_pausas_activas, name='listar_pausas_activas'),
    
    path('pausas/editar/<int:pausa_id>/', views.editar_pausa, name='editar_pausa'),
    path('pausas/eliminar/<int:pausa_id>/', views.eliminar_pausa, name='eliminar_pausa'),
    
    #empleados
    path('empleado/dashboard/', views.dashboard_empleado, name='dashboard_empleado'),
    path('empleado/campanas-asignadas/', views.campanas_asignadas, name='campanas_asignadas'),
    path('empleado/realizar-campana/', views.realizar_campana, name='realizar_campana'),
    path('empleado/registrar-pausa/', views.registrar_pausa, name='registrar_pausa'),
    path('empleado/ver-pausas/', views.ver_pausas, name='ver_pausas'),
    path('empleado/subir-evidencia/', views.subir_evidencia, name='subir_evidencia'),
    path('empleado/campanas-participadas/', views.campanas_participadas, name='campanas_participadas'),
    path('empleado/feedback/', views.feedback_empleado, name='feedback'),
    
    path('obtener-temas/', views.obtener_temas, name='obtener_temas'),
    path('obtener-temas-crucigrama/', views.obtener_temas_crucigrama, name='obtener_temas_crucigrama'),



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
