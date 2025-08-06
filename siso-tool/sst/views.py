from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Count, F
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.db.models import Subquery, OuterRef
from django.core.serializers.json import DjangoJSONEncoder
import random
import json
import io
import xlsxwriter
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from .forms import (RegistroUsuarioForm, AdminCrearUsuarioForm, AdminEditarUsuarioForm,CampañaForm, EncuestaForm, FeedbackForm, CodigoCampañaForm)
from .models import Usuario, Actividad, Campaña, CampanaAsignada, Feedback, CodigoCampaña
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from django.http import FileResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
from django.http import HttpResponse
from .models import Campaña, CampanaAsignada
from reportlab.platypus import Image
import matplotlib
matplotlib.use('Agg') 
from django.utils.timezone import localtime
from .models import RegistroPausa, Usuario
from django.contrib.auth.models import User
from django.http import JsonResponse
from .forms import CampanaAsignadaForm
from .models import PausaActiva 
from .models import SopaLetras
from .models import CampanaAsignada, RegistroPausa, PausaActiva, Calificacion, Encuesta
from sst.models import PausaActiva
from .models import MovimientoArticular
from django.db.models import Max
from .models import Crucigrama
from django.utils.timezone import now
from django.contrib import messages
from .forms import PausaActivaForm
from datetime import date 
from .forms import PausaActivaForm
from .models import TemaSopaLetras, PalabraTema,  TemaCrucigrama, DefinicionTema




Usuario = get_user_model()


# Vista de inicio / landing
def inicio(request):
    return render(request, 'inicio.html', {
        'MEDIA_URL': settings.MEDIA_URL
    })

def es_admin(user):
    return user.is_authenticated and user.cargo == 'admin'

# Vista de login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            if usuario.is_superuser:
                return redirect('admin_dashboard')  
            return redirect('dashboard_empleado')
        else:
            messages.error(request, 'Credenciales incorrectas')
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('inicio')

#REESTABLECER CONTRASEÑA
def restablecer_contraseña(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == 'POST':
        nueva = request.POST.get('password')
        confirmar = request.POST.get('confirmar')

        if nueva == confirmar:
            usuario.set_password(nueva)
            usuario.codigo_temporal = None
            usuario.save()
            messages.success(request, 'Contraseña actualizada.')
            return redirect('login')
        else:
            messages.error(request, 'Las contraseñas no coinciden.')

    return render(request, 'auth/reset_password.html', {'usuario': usuario})

#enviar codigo
def enviar_codigo(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        usuario = Usuario.objects.filter(email=correo).first()

        if not usuario:
            messages.error(request, "El correo no está registrado.")
            return redirect('enviar_codigo')

        codigo = get_random_string(length=6, allowed_chars='1234567890')
        usuario.codigo_temporal = codigo
        usuario.save()

        # Renderiza plantilla HTML personalizada
        html_content = render_to_string('auth/codigo_recuperacion.html', {
            'nombre': usuario.first_name or usuario.username,
            'codigo': codigo,
        })

        # Construye el correo con HTML
        email = EmailMultiAlternatives(
            subject="🔐 Clave Temporal de Acceso",
            body=f"Tu código temporal es: {codigo}",
            from_email="conjuntoresidencialeldorado22@gmail.com",
            to=[correo],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        request.session['correo_verificacion'] = correo
        messages.success(request, "Hemos enviado un código a tu correo.")
        return redirect('verificar_codigo')

    return render(request, 'auth/enviar_codigo.html')
                  
#RECUPERACION DE CONTRASEÑA
def solicitar_codigo(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            usuario = Usuario.objects.get(email=email)
            codigo = str(random.randint(100000, 999999))
            usuario.codigo_temporal = codigo
            usuario.fecha_codigo = timezone.now() + timedelta(minutes=10)
            usuario.save()

            send_mail(
                subject='🔐 Código de recuperación',
                message=f'Tu código temporal es: {codigo}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email]
            )

            messages.success(request, 'Código enviado. Revisa tu correo.')
            return redirect('verificar_codigo')
        except Usuario.DoesNotExist:
            messages.error(request, 'Correo no registrado.')

    return render(request, 'auth/solicitar_codigo.html')

#CODIGO DE RECUPERACION
def verificar_codigo(request):
    correo = request.session.get('correo_verificacion')  # recupera correo de la sesión

    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo')

        if not correo:
            messages.error(request, 'Correo no válido o código expirado.')
            return redirect('enviar_codigo')

        try:
            usuario = Usuario.objects.get(email=correo)
        except Usuario.DoesNotExist:
            messages.error(request, 'Correo no registrado.')
            return redirect('enviar_codigo')

        if usuario.codigo_temporal == codigo_ingresado:
            usuario.codigo_temporal = None  
            usuario.save()
            request.session['email_verificado'] = correo  
            return redirect('restablecer_contraseña', id=usuario.id)

        else:
            messages.error(request, 'Código incorrecto.')

    return render(request, 'auth/verificar_codigo.html', {'correo': correo})

#usuarios registrados
@login_required
def usuarios_registrados(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios_admin/usuarios_registrados.html', {'usuarios': usuarios})

#crear usuarios
@user_passes_test(lambda u: u.is_superuser)
def crear_usuario_admin(request):
    if request.method == 'POST':
        form = AdminCrearUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/panel/dashboard/')
    else:
        form = AdminCrearUsuarioForm()

    return render(request, 'usuarios_admin/crear_usuario_admin.html', {'form': form})

# Vista de registro de usuario
def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.username = form.cleaned_data['email']  # opcional: usa el email como username
            usuario.save()
            messages.success(request, 'Registro exitoso. Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'auth/registro.html', {'form': form})


# Vista de actividades (SG-SST)
@login_required
def lista_actividades(request):
    actividades = Actividad.objects.all()
    return render(request, 'actividades/actividades.html', {'actividades': actividades})

# ========= VISTAS ADMIN =========

@user_passes_test(lambda u: u.is_superuser)
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    total_usuarios = Usuario.objects.count()
    total_campañas = Campaña.objects.count()
    total_asignadas = CampanaAsignada.objects.count()
    asignaciones_detalle = CampanaAsignada.objects.select_related('campaña', 'empleado')
    
    return render(request, 'admin_dashboard.html', {
        'usuarios': total_usuarios,
        'campañas': total_campañas,
        'asignaciones': total_asignadas,
        'asignaciones_detalle': asignaciones_detalle
    })


@user_passes_test(lambda u: u.is_superuser)
def administrar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'admin_usuarios.html', {'usuarios': usuarios})

#listar usuarios
@user_passes_test(lambda u: u.is_superuser)
def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios_admin/listar_usuarios.html', {'usuarios': usuarios})

#crear usuarios
@user_passes_test(lambda u: u.is_superuser)
def crear_usuario(request):
    if request.method == 'POST':
        form = AdminCrearUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)        
            usuario.date_joined = timezone.now()     
            usuario.save()                        
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('listar_usuarios')
    else:
        form = AdminCrearUsuarioForm()
    return render(request, 'usuarios_admin/usuarios/crear.html', {'form': form})

#editar usuarios
@user_passes_test(lambda u: u.is_superuser)
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = AdminEditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado.')
            return redirect('listar_usuarios')
    else:
        form = AdminEditarUsuarioForm(instance=usuario)
    return render(request, 'usuarios_admin/editar_usuario.html', {'form': form})

#inhabilitar usuario
@user_passes_test(lambda u: u.is_superuser)
def inhabilitar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    usuario.is_active = False
    usuario.save()
    messages.warning(request, f'Usuario {usuario.first_name} {usuario.last_name} inhabilitado.')
    return redirect('listar_usuarios')

#habilitar usuario
@user_passes_test(lambda u: u.is_superuser)
def habilitar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    usuario.is_active = True
    usuario.save()
    messages.success(request, 'Usuario habilitado.')
    return redirect('listar_usuarios')

#exportar
def exportar_usuarios_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Usuarios"

    # Encabezados
    ws.append(['Nombre', 'Apellidos', 'Teléfono', 'Departamento', 'Ciudad', 'Dirección', 'Email', 'Rol', 'Estado'])

    # Datos
    for u in Usuario.objects.all():
        ws.append([
            u.first_name, u.last_name, u.telefono, u.departamento, u.ciudad,
            u.direccion, u.email, u.get_cargo_display(), "Activo" if u.is_active else "Inactivo"
        ])

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=usuarios.xlsx'
    wb.save(response)
    return response


def exportar_usuarios_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="usuarios_registrados.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Usuarios Registrados", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    data = [[
        'N°', 'Nombre', 'Apellidos', 'Teléfono', 'Departamento', 
        'Ciudad', 'Dirección', 'Email', 'Rol', 'Estado'
    ]]

    usuarios = Usuario.objects.all()
    for i, u in enumerate(usuarios, start=1):
        data.append([
            str(i), u.first_name, u.last_name, u.telefono, u.departamento,
            u.ciudad, u.direccion, u.email, u.get_cargo_display(),
            "Activo" if u.is_active else "Inactivo"
        ])

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
    ]))

    elements.append(table)
    doc.build(elements)

    return response


@user_passes_test(lambda u: u.is_superuser)
def crear_campaña(request):
    if request.method == 'POST':
        form = CampañaForm(request.POST, request.FILES)
        if form.is_valid():
            campaña = form.save()  # Guardar la campaña
            empleado = form.cleaned_data.get('empleado')  # Obtener empleado del formulario

            if empleado:
                CampanaAsignada.objects.create(campaña=campaña, empleado=empleado)

            return redirect('listar_campañas')
    else:
        form = CampañaForm()

    return render(request, 'campañas/crear_campaña.html', {
        'form': form
    })
    
#listar campañas
def listar_campañas(request):
    asignacion = CampanaAsignada.objects.filter(campaña=OuterRef('pk')).select_related('empleado')

    campañas = Campaña.objects.annotate(
        empleado_nombre=Subquery(asignacion.values('empleado__first_name')[:1]),
        empleado_apellido=Subquery(asignacion.values('empleado__last_name')[:1])
    )

    return render(request, 'campañas/listar_campañas.html', {'campañas': campañas})

#editar campaña
def editar_campaña(request, id):
    campaña = get_object_or_404(Campaña, id=id)

    if request.method == 'POST':
        form = CampañaForm(request.POST, request.FILES, instance=campaña)
        if form.is_valid():
            form.save()
            return redirect('listar_campañas')
    else:
        form = CampañaForm(instance=campaña)

    return render(request, 'campañas/editar_campaña.html', {
        'form': form,
        'campaña': campaña
    })

# Eliminar campaña
def eliminar_campaña(request, id):
    campaña = get_object_or_404(Campaña, id=id)
    
    if request.method == 'POST':
        campaña.delete()
        return redirect('listar_campañas')
    
    return render(request, 'campañas/eliminar_campaña.html', {'campaña': campaña})

#asignar campaña
def campañas_asignadas(request):
    asignaciones = CampanaAsignada.objects.select_related('campaña', 'empleado').all()
    return render(request, 'estadisticas/campanias_asignadas.html', {'asignaciones': asignaciones})


#exportar
def generar_grafico(datos_dict, titulo):
    fig, ax = plt.subplots()
    labels = list(datos_dict.keys())
    values = list(datos_dict.values())

    ax.bar(labels, values, color='teal')
    ax.set_title(titulo)
    ax.set_ylabel('Cantidad')
    ax.set_xlabel('Categoría')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

def exportar_campañas_pdf(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Título
    elements.append(Paragraph("Campañas Creadas", styles['Title']))
    elements.append(Spacer(1, 12))

    # Cabecera tabla
    data = [["ID", "Código", "Nombre", "Detalle", "Estado", "Periodicidad", "Fecha"]]

    campañas = Campaña.objects.all()

    estado_count = {}
    periodicidad_count = {}

    for c in campañas:
        data.append([
            str(c.id),
            c.codigo.codigo,
            c.codigo.nombre,
            c.detalle,
            c.estado,
            c.periodicidad,
            localtime(c.fecha_creacion).strftime("%Y-%m-%d %H:%M")
        ])
        estado_count[c.estado] = estado_count.get(c.estado, 0) + 1
        periodicidad_count[c.periodicidad] = periodicidad_count.get(c.periodicidad, 0) + 1

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B547E")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
    ]))

    elements.append(table)
    elements.append(PageBreak())

    # Gráficos
    grafico_estado = generar_grafico(estado_count, "Distribución por Estado de Campañas")
    elements.append(Paragraph("Gráfico: Estado de Campañas", styles['Heading2']))
    elements.append(Spacer(1, 10))
    elements.append(Image(grafico_estado, width=450, height=200))
    elements.append(Spacer(1, 20))
    grafico_periodicidad = generar_grafico(periodicidad_count, "Distribución por Periodicidad")
    elements.append(Paragraph("Gráfico: Periodicidad de Campañas", styles['Heading2']))
    elements.append(Spacer(1, 10))
    elements.append(Image(grafico_periodicidad, width=450, height=200))

    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(
    buffer,
    content_type='application/pdf',
    headers={"Content-Disposition": 'inline; filename="campañas_creadas.pdf"'}
)
    
    
def exportar_campañas_excel(request):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})

    # Hoja 1: Tabla de campañas
    ws1 = workbook.add_worksheet("Campañas")

    headers = ["ID", "Código", "Nombre", "Detalle", "Estado", "Periodicidad", "Fecha"]
    for col_num, header in enumerate(headers):
        ws1.write(0, col_num, header)

    campañas = Campaña.objects.all()
    estado_count = {}
    periodicidad_count = {}

    for row_num, c in enumerate(campañas, start=1):
        ws1.write(row_num, 0, c.id)
        ws1.write(row_num, 1, c.codigo.codigo)
        ws1.write(row_num, 2, c.codigo.nombre)
        ws1.write(row_num, 3, c.detalle)
        ws1.write(row_num, 4, c.estado)
        ws1.write(row_num, 5, c.periodicidad)
        ws1.write(row_num, 6, c.fecha_creacion.strftime("%Y-%m-%d %H:%M"))

        estado_count[c.estado] = estado_count.get(c.estado, 0) + 1
        periodicidad_count[c.periodicidad] = periodicidad_count.get(c.periodicidad, 0) + 1

    # Hoja 2: Gráficas
    ws2 = workbook.add_worksheet("Gráficas")

    # Estado
    ws2.write(0, 0, "Estado")
    ws2.write(0, 1, "Cantidad")
    for i, (estado, count) in enumerate(estado_count.items(), start=1):
        ws2.write(i, 0, estado)
        ws2.write(i, 1, count)

    chart1 = workbook.add_chart({'type': 'column'})
    chart1.add_series({
        'name': 'Estado',
        'categories': ['Gráficas', 1, 0, len(estado_count), 0],
        'values':     ['Gráficas', 1, 1, len(estado_count), 1],
    })
    chart1.set_title({'name': 'Distribución por Estado'})
    chart1.set_style(10)
    ws2.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})

    # Periodicidad
    start_row = len(estado_count) + 3
    ws2.write(start_row, 0, "Periodicidad")
    ws2.write(start_row, 1, "Cantidad")

    for i, (p, count) in enumerate(periodicidad_count.items(), start=start_row + 1):
        ws2.write(i, 0, p)
        ws2.write(i, 1, count)

    chart2 = workbook.add_chart({'type': 'column'})
    chart2.add_series({
        'name': 'Periodicidad',
        'categories': ['Gráficas', start_row + 1, 0, i, 0],
        'values':     ['Gráficas', start_row + 1, 1, i, 1],
    })
    chart2.set_title({'name': 'Distribución por Periodicidad'})
    chart2.set_style(11)
    ws2.insert_chart('D20', chart2, {'x_offset': 25, 'y_offset': 10})

    workbook.close()
    output.seek(0)

    return HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=campañas_creadas.xlsx'}
    )
#crear codigos
def crear_codigo(request):
    if request.method == 'POST':
        form = CodigoCampañaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_codigos')  
    else:
        form = CodigoCampañaForm()
    
    return render(request, 'codigos/crear_codigo.html', {'form': form})

#editar codigo
def editar_codigo(request, id):
    codigo = get_object_or_404(CodigoCampaña, id=id)

    if request.method == 'POST':
        form = CodigoCampañaForm(request.POST, instance=codigo)
        if form.is_valid():
            form.save()
            return redirect('listar_codigos')  
    else:
        form = CodigoCampañaForm(instance=codigo)

    return render(request, 'codigos/editar_codigo.html', {'form': form})

#eliminar codigo
def eliminar_codigo(request, id):
    codigo = get_object_or_404(CodigoCampaña, id=id)
    
    if request.method == 'POST':
        codigo.delete()
        return redirect('listar_codigos')

#listar codigos
def listar_codigos(request):
    codigos = CodigoCampaña.objects.all()
    return render(request, 'codigos/listar_codigos.html', {'codigos': codigos})

#estadisticas
def estadisticas_pausas(request):
    total_empleados = Usuario.objects.filter(cargo='empleado').count()
    empleados_con_pausa = RegistroPausa.objects.values('empleado').distinct().count()
    empleados_sin_pausa = total_empleados - empleados_con_pausa

    pausas = RegistroPausa.objects.select_related('empleado').all()

    return render(request, 'estadisticas/estadisticas_pausas.html', {
        'total_empleados': total_empleados,
        'empleados_con_pausa': empleados_con_pausa,
        'empleados_sin_pausa': empleados_sin_pausa,
        'pausas': pausas,
    })

def estadisticas_menu(request):
    total_campañas = Campaña.objects.count()
    total_asignadas = Campaña.objects.filter(estado='Asignada').count()
    realizadas = Campaña.objects.filter(estado='Realizada').count()
    sin_realizar = Campaña.objects.filter(estado='Sin Realizar').count()
    empleados_con_pausa = 0  
    empleados_sin_pausa = 0  

    return render(request, 'estadisticas/estadisticas_menu.html', {
        'total_campañas': total_campañas,
        'total_asignadas': total_asignadas,
        'realizadas': realizadas,
        'sin_realizar': sin_realizar,
        'empleados_con_pausa': empleados_con_pausa,
        'empleados_sin_pausa': empleados_sin_pausa
    })
def campañas_creadas(request):
    campañas = Campaña.objects.select_related('codigo').all()

    campañas_data = [
        {
            'nombre': c.codigo.nombre,
            'estado': c.estado,
            'periodicidad': c.periodicidad
        }
        for c in campañas
    ]

    return render(request, 'estadisticas/campañas_creadas.html', {
        'campañas': campañas,
        'campañas_json': json.dumps(campañas_data, cls=DjangoJSONEncoder)
    })
    
def campanias_asignadas(request):
    asignadas = CampanaAsignada.objects.select_related('campaña', 'empleado').all()

    resumen = (
        asignadas
        .values(nombre=F('campaña__codigo__nombre'))
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')
    )

    resumen_json = json.dumps(list(resumen))  

    return render(request, 'estadisticas/campanias_asignadas.html', {
        'asignadas': asignadas,
        'resumen_asignaciones': resumen_json  
    })
    
def campañas_realizadas(request):
    campañas_realizadas = Campaña.objects.filter(estado__iexact='Realizada')
    return render(request, 'estadisticas/campanias_realizadas.html', {
        'campañas_realizadas': campañas_realizadas
    })
    
def campañas_sin_realizar(request):
    campañas_sin_realizar = Campaña.objects.filter(estado__iexact='Sin Realizar')
    return render(request, 'estadisticas/campanias_sin_realizar.html', {
        'campañas_sin_realizar': campañas_sin_realizar
    })


def estadisticas_campañas(request):
    campañas = Campaña.objects.all()

    total_asignadas = CampanaAsignada.objects.count()
    total_realizadas = CampanaAsignada.objects.filter(realizada=True).count()
    total_sin_realizar = CampanaAsignada.objects.filter(realizada=False).count()

    datos_tarjetas = [
        {'titulo': 'Creadas', 'total': campañas.count(), 'color': 'primary', 'url': 'campañas_creadas'},
        {'titulo': 'Asignadas', 'total': total_asignadas, 'color': 'info', 'url': 'campanias_asignadas'},
        {'titulo': 'Realizadas', 'total': total_realizadas, 'color': 'success', 'url': 'campañas_realizadas'},
        {'titulo': 'Sin Realizar', 'total': total_sin_realizar, 'color': 'danger', 'url': 'campañas_sin_realizar'},
    ]

    return render(request, 'estadisticas/estadisticas_campañas.html', {
        'campañas': campañas,
        'datos_tarjetas': datos_tarjetas
    })
    

# Temas predefinidos con palabras para sopa de letras y crucigramas
TEMAS_SOPA = {
    'salud': ['vitamina', 'agua', 'dieta', 'deporte', 'higiene'],
    'naturaleza': ['arbol', 'rio', 'sol', 'nube', 'montaña'],
    'animales': ['perro', 'gato', 'tigre', 'pez', 'aguila'],
}

TEMAS_CRUCIGRAMA = {
    'frutas': {
        'manzana': 'Fruta roja o verde, crece en árboles.',
        'pera': 'Fruta jugosa, forma de bombilla.',
        'banana': 'Fruta alargada y amarilla.'
    },
    'cuerpo': {
        'corazon': 'Órgano que bombea sangre.',
        'ojo': 'Permite la visión.',
        'pulmon': 'Órgano para respirar.'
    }
}

def crear_pausa(request):
    TIPOS_PAUSA_NOMBRE = {
        'sopa': 'Sopa de Letras',
        'crucigrama': 'Crucigrama',
        'movimiento': 'Movimiento Articular'
    }

    if request.method == 'POST':
        tipo = request.POST.get('tipo')

        # ----------- 🧩 Sopa de Letras ------------
        if tipo == 'sopa':
            tema_sopa_id = request.POST.get('tema_sopa')
            if not tema_sopa_id:
                messages.error(request, "❌ Debes seleccionar un tema para la sopa de letras.")
                return render(request, 'pausas_Activas/crear_pausa.html')

            try:
                tema_obj = TemaSopaLetras.objects.get(id=int(tema_sopa_id))
            except TemaSopaLetras.DoesNotExist:
                messages.error(request, "❌ Tema no válido.")
                return render(request, 'pausas_Activas/crear_pausa.html')

            palabras = list(tema_obj.palabras.values_list('texto', flat=True))
            if not palabras:
                messages.error(request, "❌ El tema no tiene palabras registradas.")
                return render(request, 'pausas_Activas/crear_pausa.html')

            palabras_random = random.sample(palabras, min(len(palabras), 10))
            titulo = f"Sopa de Letras - {tema_obj.nombre.capitalize()}"
            instrucciones = f"Encuentra las siguientes palabras relacionadas con {tema_obj.nombre}."
            nombre = titulo
            descripcion = instrucciones
            cargo = "empleado"

        # ----------- ✏ Crucigrama ------------
        elif tipo == 'crucigrama':
            tema_cruci_id = request.POST.get('tema_crucigrama')
            if not tema_cruci_id:
                messages.error(request, "❌ Debes seleccionar un tema para el crucigrama.")
                return render(request, 'pausas_Activas/crear_pausa.html')

            try:
                tema_obj = TemaCrucigrama.objects.get(id=int(tema_cruci_id))
            except TemaCrucigrama.DoesNotExist:
                messages.error(request, "❌ Tema no válido.")
                return render(request, 'pausas_Activas/crear_pausa.html')

            definiciones_qs = tema_obj.definiciones.all()
            if not definiciones_qs.exists():
                messages.error(request, "❌ El tema seleccionado no tiene definiciones.")
                return render(request, 'pausas_Activas/crear_pausa.html')

            definiciones_dict = {d.palabra: d.definicion for d in definiciones_qs}
            definiciones_json = json.dumps(definiciones_dict, ensure_ascii=False)  # ✅ SERIALIZACIÓN AQUÍ

            titulo = f"Crucigrama - {tema_obj.nombre.capitalize()}"
            instrucciones = f"Completa el crucigrama relacionado con {tema_obj.nombre}."
            nombre = titulo
            descripcion = instrucciones
            cargo = "empleado"

        # ----------- 🧘 Movimiento Articular ------------
        elif tipo == 'movimiento':
            nombre_mov = request.POST.get('nombre_mov')
            descripcion_mov = request.POST.get('descripcion_mov')
            imagen = request.FILES.get('imagen')

            if not nombre_mov or not descripcion_mov or not imagen:
                messages.error(request, "❌ Todos los campos del movimiento articular son obligatorios.")
                return render(request, 'pausas_Activas/crear_pausa.html')

            nombre = nombre_mov
            descripcion = descripcion_mov
            cargo = "general"

        else:
            messages.error(request, "❌ Tipo de pausa no válido.")
            return redirect('crear_pausa')

        # ------- Creación de PausaActiva -------
        pausa = PausaActiva.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            tipo=tipo,
            cargo=cargo,
            fecha=now()
        )

        request.session['pausa_id'] = pausa.id

        # ---- Crea tipo específico asociado ----
        if tipo == 'sopa':
            SopaLetras.objects.create(
                titulo=titulo,
                instrucciones=instrucciones,
                palabras=", ".join(palabras_random),
                pausa=pausa
            )

        elif tipo == 'crucigrama':
            Crucigrama.objects.create(
                titulo=titulo,
                instrucciones=instrucciones,
                definiciones=definiciones_json,  
                pausa=pausa
            )

        elif tipo == 'movimiento':
            orden = MovimientoArticular.objects.aggregate(Max('orden'))['orden__max'] or 0
            MovimientoArticular.objects.create(
                nombre=nombre_mov,
                descripcion=descripcion_mov,
                imagen=imagen,
                orden=orden + 1,
                pausa=pausa
            )

        return render(request, 'pausas_Activas/crear_pausa.html', {
            'pausa_creada': True,
            'nombre_pausa': TIPOS_PAUSA_NOMBRE.get(tipo, 'Pausa Activa')
        })

    return render(request, 'pausas_Activas/crear_pausa.html')

def generar_palabras_para_sopa(tema_id):
    tema = TemaSopaLetras.objects.get(id=tema_id)
    palabras = list(tema.palabras.values_list('texto', flat=True))
    return random.sample(palabras, 10) if len(palabras) >= 10 else palabras

def obtener_temas(request):
    temas = TemaSopaLetras.objects.all().values('id', 'nombre')
    return JsonResponse({'temas': list(temas)})

def obtener_temas_crucigrama(request):
    temas = list(TemaCrucigrama.objects.values('id', 'nombre'))
    return JsonResponse({'temas': temas})
#-----------------------------------------------------------------------------------#
def editar_pausa(request, pausa_id):
    pausa = get_object_or_404(PausaActiva, id=pausa_id)
    if request.method == 'POST':
        form = PausaActivaForm(request.POST, instance=pausa)
        if form.is_valid():
            form.save()
            return redirect('ver_pausas_creadas')  # Asegúrate de tener esta vista nombrada así
    else:
        form = PausaActivaForm(instance=pausa)
    return render(request, 'pausas_Activas/editar_pausa.html', {'form': form})

def eliminar_pausa(request, pausa_id):
    pausa = get_object_or_404(PausaActiva, id=pausa_id)
    if request.method == 'POST':
        pausa.delete()
        return redirect('ver_pausas_creadas')
    return render(request, 'pausas_Activas/eliminar_pausa.html', {'pausa': pausa})

#-----------------------------------------------------------------------------------#
def registro_pausas(request):
    registros = RegistroPausa.objects.select_related('empleado', 'pausa').order_by('-fecha')
    return render(request, 'pausas_Activas/registro_pausas.html', {
        'registros': registros
    })
    
def registrar_pausa(request):
    tipo = request.GET.get("tipo") or request.POST.get("tipo")

    # Si se confirmó la pausa
    if request.method == "POST" and request.POST.get("confirmar_pausa"):
        empleado = request.user
        pausa = PausaActiva.objects.filter(tipo=tipo).last()

        if pausa:
            RegistroPausa.objects.create(empleado=empleado, pausa=pausa)
            return redirect('registro_pausas')  # Asegúrate de que esta ruta exista

    # Mostrar la sopa de letras
    if tipo == "sopa":
        pausa = PausaActiva.objects.filter(tipo="sopa").last()
        if not pausa:
            return render(request, 'empleados/registrar_pausa.html', {'tipo': tipo, 'error': 'No hay sopas disponibles.'})

        sopa = SopaLetras.objects.get(pausa=pausa)

        # Convierte la matriz (cadena tipo "A,B,C,...") en lista de listas
        plano = sopa.matriz.replace(',', '')
        tamano = sopa.tamano
        matriz = [list(plano[i * tamano:(i + 1) * tamano]) for i in range(tamano)]
        palabras = sopa.palabras.split(',')

        return render(request, 'empleados/registrar_pausa.html', {
            'tipo': tipo,
            'matriz': matriz,
            'palabras': palabras
        })

    return render(request, 'empleados/registrar_pausa.html', {
        'tipo': tipo
    })
#--------------------------------------------------------------------------------------#
def asignacion_pausas(request):
    return render(request, 'pausas_Activas/asignacion_pausas.html')

def ver_pausas_creadas(request):
    pausas = PausaActiva.objects.all().order_by('-fecha')
    return render(request, 'pausas_activas/ver_pausas_creadas.html', {'pausas': pausas})

def pausas_crear_menu(request):
    return render(request, 'pausas_Activas/crear_pausa_menu.html')

def estadisticas_pausas(request):
    total_pausas_creadas = PausaActiva.objects.count()
    
    empleados_con_pausa = RegistroPausa.objects.values('empleado').distinct().count()
    total_empleados = Usuario.objects.filter(cargo='empleado').count()
    empleados_sin_pausa = total_empleados - empleados_con_pausa

    return render(request, 'estadisticas/estadisticas_pausas.html', {
        'total_pausas_creadas': total_pausas_creadas,
        'empleados_con_pausa': empleados_con_pausa,
        'empleados_sin_pausa': empleados_sin_pausa,
        'total_empleados': total_empleados
    })

def listar_pausas_activas(request):
    pausas = PausaActiva.objects.all().order_by('-fecha')
    return render(request, 'pausas_Activas/listar_pausas.html', {
        'pausas': pausas
    })
    
    
# ========= VISTAS EMPLEADO =========

@login_required
def dashboard_empleado(request):
    usuario = request.user

    campañas_participadas = CampanaAsignada.objects.filter(empleado=usuario, realizada=True)
    pausas_activas = RegistroPausa.objects.filter(empleado=usuario).order_by('-fecha')[:5]
    hoy = timezone.now().date()
    campañas_hoy = CampanaAsignada.objects.filter(empleado=usuario, campaña__fecha_asignacion=hoy)
    calificaciones = Feedback.objects.filter(empleado=usuario)

    return render(request, 'dashboard_empleado.html', {
        'campañas_participadas': campañas_participadas,
        'pausas_activas': pausas_activas,
        'campañas_hoy': campañas_hoy,
        'calificaciones': calificaciones,
    })


@login_required
def campanas_asignadas(request):
    asignadas = CampanaAsignada.objects.filter(empleado=request.user)
    return render(request, 'empleados/campanas_asignadas.html', {'asignadas': asignadas})

@login_required
def realizar_campana(request):
    if request.method == 'POST':
        # Aquí procesas los datos enviados por el formulario
        return redirect('dashboard_empleado')
    return render(request, 'empleado/realizar_campana.html')


def registrar_pausa(request):
    if request.method == 'POST':
        form = PausaActivaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard_empleado')
    else:
        form = PausaActivaForm()

    tipo = request.GET.get('tipo')

    if tipo == 'sopa':
        temas = TemaSopaLetras.objects.all()
        return render(request, 'empleados/partials/sopa_form.html', {'temas': temas})
    
    elif tipo == 'crucigrama':
        temas = TemaCrucigrama.objects.all()
        return render(request, 'empleados/partials/crucigrama_form.html', {'temas': temas})
    
    elif tipo == 'movimiento':
        return render(request, 'empleados/partials/movimiento_form.html')

    # Render completo inicial si no hay tipo
    return render(request, 'empleados/registrar_pausa.html', {'form': form})

@login_required
def ver_pausas(request):
    pausas = RegistroPausa.objects.filter(empleado=request.user)
    return render(request, 'empleados/ver_pausas.html', {'pausas': pausas})


@login_required
def subir_evidencia(request):
    if request.method == 'POST':
        evidencia = request.FILES.get('evidencia')
        # Aquí puedes crear una Encuesta o Registro con evidencia
        Encuesta.objects.create(
            empleado=request.user,
            evidencia=evidencia,
            respuestas="Evidencia sin encuesta",
            fecha=timezone.now()
        )
        return redirect('dashboard_empleado')
    return redirect('dashboard_empleado')

def campanas_participadas(request):
    participadas = Campaña.objects.filter(participantes=request.user)
    return render(request, 'campanas_participadas.html', {'participadas': participadas})

def feedback_empleado(request):
    calificaciones = Feedback.objects.filter(empleado=request.user)
    return render(request, 'empleados/feedback.html', {'calificaciones': calificaciones})





@login_required
def campañas_asignadas(request):
    asignadas = CampanaAsignada.objects.filter(empleado=request.user)
    return render(request, 'campañas_asignadas.html', {'asignadas': asignadas})

@login_required
def encuesta_campaña(request, campaña_id):
    asignacion = get_object_or_404(CampanaAsignada, campaña_id=campaña_id, empleado=request.user)
    if request.method == 'POST':
        form = EncuestaForm(request.POST, request.FILES)
        if form.is_valid():
            encuesta = form.save(commit=False)
            encuesta.campaña_asignada = asignacion
            encuesta.save()
            messages.success(request, 'Encuesta enviada con éxito.')
            return redirect('dashboard_empleado')
    else:
        form = EncuestaForm()
    return render(request, 'encuesta_campaña.html', {'form': form, 'campaña': asignacion.campaña})

@login_required
def feedback_campaña(request, campaña_id):
    asignacion = get_object_or_404(CampanaAsignada, campaña_id=campaña_id, empleado=request.user)
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.campaña_asignada = asignacion
            feedback.save()
            messages.success(request, 'Gracias por tu calificación.')
            return redirect('dashboard_empleado')
    else:
        form = FeedbackForm()
    return render(request, 'feedback_campaña.html', {'form': form, 'campaña': asignacion.campaña})
