from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Cliente, Empresa

# ==================== CLIENTE ====================
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'rut', 'nombre_completo', 'telefono_formateado', 
        'email', 'comuna_info', 'region_info', 'estado'
    )  # Añadido 'estado' aquí
    list_filter = ('estado', 'comuna_id__region', 'comuna_id')
    search_fields = (
        'rut', 'nombres', 'ap_paterno', 'ap_materno', 
        'email', 'telefono', 'direccion'
    )
    list_editable = ('estado',)
    ordering = ('ap_paterno', 'ap_materno', 'nombres')
    actions = ['export_to_csv', 'activar_clientes', 'desactivar_clientes']
    
    fieldsets = (
        ('Información Tributaria', {
            'fields': ('rut', 'estado')
        }),
        ('Información Personal', {
            'fields': ('nombres', 'ap_paterno', 'ap_materno')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email')
        }),
        ('Dirección', {
            'fields': ('direccion', 'comuna_id')
        }),
    )

    def nombre_completo(self, obj):
        return f"{obj.nombres} {obj.ap_paterno} {obj.ap_materno}"
    nombre_completo.short_description = 'Nombre Completo'
    nombre_completo.admin_order_field = 'ap_paterno'

    def telefono_formateado(self, obj):
        if obj.telefono:
            if obj.telefono.startswith('+56'):
                return f"{obj.telefono[:3]} {obj.telefono[3:5]} {obj.telefono[5:8]} {obj.telefono[8:]}"
            elif obj.telefono.startswith('56'):
                return f"+{obj.telefono[:2]} {obj.telefono[2:4]} {obj.telefono[4:7]} {obj.telefono[7:]}"
            elif obj.telefono.startswith('9'):
                return f"+56 {obj.telefono[:1]} {obj.telefono[1:4]} {obj.telefono[4:]}"
        return obj.telefono
    telefono_formateado.short_description = 'Teléfono'

    def comuna_info(self, obj):
        return obj.comuna_id.nombre_comuna if obj.comuna_id else "Sin comuna"
    comuna_info.short_description = 'Comuna'
    comuna_info.admin_order_field = 'comuna_id__nombre_comuna'

    def region_info(self, obj):
        if obj.comuna_id and obj.comuna_id.region:
            return obj.comuna_id.region.nombre_region
        return "Sin región"
    region_info.short_description = 'Región'
    region_info.admin_order_field = 'comuna_id__region__nombre_region'

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="clientes.csv"'
        response.write('\ufeff')  # BOM para UTF-8

        writer = csv.writer(response)
        writer.writerow([
            'RUT', 'Nombres', 'Apellido Paterno', 'Apellido Materno',
            'Teléfono', 'Email', 'Dirección', 'Comuna', 'Región', 'Estado',
            'Fecha Creación', 'Fecha Actualización'
        ])

        for cliente in queryset:
            writer.writerow([
                cliente.rut,
                cliente.nombres,
                cliente.ap_paterno,
                cliente.ap_materno,
                cliente.telefono,
                cliente.email,
                cliente.direccion,
                cliente.comuna_id.nombre_comuna if cliente.comuna_id else '',
                cliente.comuna_id.region.nombre_region if cliente.comuna_id and cliente.comuna_id.region else '',
                'Activo' if cliente.estado else 'Inactivo',
                cliente.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
                cliente.fecha_actualizacion.strftime("%d/%m/%Y %H:%M")
            ])

        return response
    export_to_csv.short_description = "Exportar seleccionados a CSV"

    def activar_clientes(self, request, queryset):
        updated = queryset.update(estado=True)
        self.message_user(
            request, 
            f"{updated} cliente(s) marcado(s) como activo(s)."
        )
    activar_clientes.short_description = "Activar clientes seleccionados"

    def desactivar_clientes(self, request, queryset):
        updated = queryset.update(estado=False)
        self.message_user(
            request, 
            f"{updated} cliente(s) marcado(s) como inactivo(s)."
        )
    desactivar_clientes.short_description = "Desactivar clientes seleccionados"

# ==================== EMPRESA ====================
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = (
        'rut_empresa', 'nombre_empresa', 'razon_social_abreviada',
        'representante_info', 'comuna_info', 'region_info', 'estado'
    )  # Añadido 'estado' aquí
    list_filter = ('estado', 'comuna_id__region', 'comuna_id')
    search_fields = (
        'rut_empresa', 'nombre_empresa', 'razon_social', 'giro',
        'direccion', 'telefono', 'email'
    )
    list_editable = ('estado',)
    ordering = ('nombre_empresa',)
    actions = ['export_to_csv', 'activar_empresas', 'desactivar_empresas']
    raw_id_fields = ('representante_id',)
    autocomplete_fields = ('representante_id',)
    
    fieldsets = (
        ('Información Tributaria', {
            'fields': ('rut_empresa', 'razon_social', 'giro', 'estado')
        }),
        ('Información Comercial', {
            'fields': ('nombre_empresa',)
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'direccion', 'comuna_id')
        }),
        ('Representante Legal', {
            'fields': ('representante_id',)
        }),
    )

    def razon_social_abreviada(self, obj):
        if len(obj.razon_social) > 30:
            return f"{obj.razon_social[:30]}..."
        return obj.razon_social
    razon_social_abreviada.short_description = 'Razón Social'
    razon_social_abreviada.admin_order_field = 'razon_social'

    def representante_info(self, obj):
        if obj.representante_id:
            return f"{obj.representante_id.nombres} {obj.representante_id.ap_paterno} ({obj.representante_id.rut})"
        return "Sin representante"
    representante_info.short_description = 'Representante'
    representante_info.admin_order_field = 'representante_id__nombres'

    def comuna_info(self, obj):
        return obj.comuna_id.nombre_comuna if obj.comuna_id else "Sin comuna"
    comuna_info.short_description = 'Comuna'
    comuna_info.admin_order_field = 'comuna_id__nombre_comuna'

    def region_info(self, obj):
        if obj.comuna_id and obj.comuna_id.region:
            return obj.comuna_id.region.nombre_region
        return "Sin región"
    region_info.short_description = 'Región'
    region_info.admin_order_field = 'comuna_id__region__nombre_region'

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="empresas.csv"'
        response.write('\ufeff')  # BOM para UTF-8

        writer = csv.writer(response)
        writer.writerow([
            'RUT Empresa', 'Nombre Empresa', 'Razón Social', 'Giro',
            'Dirección', 'Teléfono', 'Email', 'Comuna', 'Región',
            'Representante', 'RUT Representante', 'Teléfono Representante',
            'Email Representante', 'Estado', 'Fecha Creación', 'Fecha Actualización'
        ])

        for empresa in queryset:
            # Información del representante
            rep_rut = rep_nombre = rep_telefono = rep_email = ''
            if empresa.representante_id:
                rep_rut = empresa.representante_id.rut
                rep_nombre = f"{empresa.representante_id.nombres} {empresa.representante_id.ap_paterno} {empresa.representante_id.ap_materno}"
                rep_telefono = empresa.representante_id.telefono
                rep_email = empresa.representante_id.email

            writer.writerow([
                empresa.rut_empresa,
                empresa.nombre_empresa,
                empresa.razon_social,
                empresa.giro,
                empresa.direccion,
                empresa.telefono,
                empresa.email,
                empresa.comuna_id.nombre_comuna if empresa.comuna_id else '',
                empresa.comuna_id.region.nombre_region if empresa.comuna_id and empresa.comuna_id.region else '',
                rep_nombre,
                rep_rut,
                rep_telefono,
                rep_email,
                'Activa' if empresa.estado else 'Inactiva',
                empresa.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
                empresa.fecha_actualizacion.strftime("%d/%m/%Y %H:%M")
            ])

        return response
    export_to_csv.short_description = "Exportar seleccionados a CSV"

    def activar_empresas(self, request, queryset):
        updated = queryset.update(estado=True)
        self.message_user(
            request, 
            f"{updated} empresa(s) marcada(s) como activa(s)."
        )
    activar_empresas.short_description = "Activar empresas seleccionadas"

    def desactivar_empresas(self, request, queryset):
        updated = queryset.update(estado=False)
        self.message_user(
            request, 
            f"{updated} empresa(s) marcada(s) como inactiva(s)."
        )
    desactivar_empresas.short_description = "Desactivar empresas seleccionadas"

    def get_queryset(self, request):
        """Optimizar consultas con select_related y prefetch_related"""
        return super().get_queryset(request).select_related(
            'comuna_id__region', 
            'representante_id'
        )