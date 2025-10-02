from django.contrib import admin
from .models import Usuario, Perfil

class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'  # <- aquí va el nombre correcto del campo en Perfil

class UsuarioAdmin(admin.ModelAdmin):
    inlines = (PerfilInline,)
    list_display = ('first_name', 'last_name', 'cedula', 'email', 'cargo', 'telefono_display', 'departamento_display', 'ciudad_display')

    def telefono_display(self, obj):
        return obj.perfil.telefono if hasattr(obj, 'perfil') else '-'
    telefono_display.short_description = 'Teléfono'

    def departamento_display(self, obj):
        return obj.perfil.departamento if hasattr(obj, 'perfil') else '-'
    departamento_display.short_description = 'Departamento'

    def ciudad_display(self, obj):
        return obj.perfil.ciudad if hasattr(obj, 'perfil') else '-'
    ciudad_display.short_description = 'Ciudad'

admin.site.register(Usuario, UsuarioAdmin)
