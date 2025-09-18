from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Caja, Venta, ItemVenta, DocumentoTributarioElectronico, ItemDocumento

# ==================== CAJA ====================
@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = (
        'numero_caja', 'nombre_caja', 'sucursal_info', 'usuario_info', 
        'estado', 'esta_asignada'
    )
    list_filter = ('estado', 'esta_asignada', 'sucursal_id')
    search_fields = (
        'numero_caja', 'nombre_caja', 'sucursal_id__nombre_sucursal',
        'usuario_id__username', 'usuario_id__first_name', 'usuario_id__last_name'
    )
    list_editable = ('estado', 'esta_asignada')
    ordering = ('sucursal_id__nombre_sucursal', 'numero_caja')
    actions = ['export_to_csv', 'activar_cajas', 'desactivar_cajas', 'marcar_asignadas', 'marcar_no_asignadas']
    raw_id_fields = ('usuario_id',)
    autocomplete_fields = ('usuario_id', 'sucursal_id')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_caja', 'nombre_caja', 'sucursal_id')
        }),
        ('Estado y Asignación', {
            'fields': ('estado', 'esta_asignada', 'usuario_id')
        }),
    )

    def sucursal_info(self, obj):
        return obj.sucursal_id.nombre_sucursal if obj.sucursal_id else "Sin sucursal"
    sucursal_info.short_description = 'Sucursal'
    sucursal_info.admin_order_field = 'sucursal_id__nombre_sucursal'

    def usuario_info(self, obj):
        if obj.usuario_id:
            return f"{obj.usuario_id.get_full_name()} ({obj.usuario_id.username})"
        return "Sin usuario"
    usuario_info.short_description = 'Usuario asignado'
    usuario_info.admin_order_field = 'usuario_id__username'

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cajas.csv"'
        response.write('\ufeff')  # BOM para UTF-8

        writer = csv.writer(response)
        writer.writerow([
            'Número Caja', 'Nombre Caja', 'Sucursal', 'Usuario', 
            'Estado', 'Asignada', 'Fecha Creación'
        ])

        for caja in queryset:
            writer.writerow([
                caja.numero_caja,
                caja.nombre_caja,
                caja.sucursal_id.nombre_sucursal if caja.sucursal_id else '',
                f"{caja.usuario_id.get_full_name()} ({caja.usuario_id.username})" if caja.usuario_id else '',
                'Activa' if caja.estado else 'Inactiva',
                'Asignada' if caja.esta_asignada else 'No asignada',
                caja.fecha_creacion.strftime("%d/%m/%Y %H:%M") if hasattr(caja, 'fecha_creacion') else ''
            ])

        return response
    export_to_csv.short_description = "Exportar seleccionados a CSV"

    def activar_cajas(self, request, queryset):
        updated = queryset.update(estado=True)
        self.message_user(
            request, 
            f"{updated} caja(s) marcada(s) como activa(s)."
        )
    activar_cajas.short_description = "Activar cajas seleccionadas"

    def desactivar_cajas(self, request, queryset):
        updated = queryset.update(estado=False)
        self.message_user(
            request, 
            f"{updated} caja(s) marcada(s) como inactiva(s)."
        )
    desactivar_cajas.short_description = "Desactivar cajas seleccionadas"

    def marcar_asignadas(self, request, queryset):
        updated = queryset.update(esta_asignada=True)
        self.message_user(
            request, 
            f"{updated} caja(s) marcada(s) como asignada(s)."
        )
    marcar_asignadas.short_description = "Marcar como asignadas"

    def marcar_no_asignadas(self, request, queryset):
        updated = queryset.update(esta_asignada=False)
        self.message_user(
            request, 
            f"{updated} caja(s) marcada(s) como no asignada(s)."
        )
    marcar_no_asignadas.short_description = "Marcar como no asignadas"

    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related(
            'sucursal_id', 
            'usuario_id'
        )


# ==================== VENTA ====================
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'fecha_venta_formateada', 'total_venta', 'total_neto',
        'total_iva', 'cliente_info', 'empresa_info', 'caja_info', 
        'usuario_info', 'estado'
    )
    list_filter = ('estado', 'fecha_venta', 'caja_id__sucursal_id', 'caja_id')
    search_fields = (
        'id', 'cliente_id__rut', 'cliente_id__nombres', 
        'cliente_id__ap_paterno', 'cliente_id__ap_materno',
        'empresa_id__rut_empresa', 'empresa_id__nombre_empresa',
        'caja_id__numero_caja', 'usuario_id__username'
    )
    list_editable = ('estado',)
    ordering = ('-fecha_venta',)
    actions = ['export_to_csv', 'activar_ventas', 'anular_ventas']
    raw_id_fields = ('cliente_id', 'empresa_id', 'caja_id', 'usuario_id')
    autocomplete_fields = ('cliente_id', 'empresa_id', 'caja_id', 'usuario_id')
    readonly_fields = ('fecha_venta',)
    
    fieldsets = (
        ('Información de la Venta', {
            'fields': ('fecha_venta', 'total_neto', 'total_iva', 
                      'total_venta', 'total_descuento', 'estado')
        }),
        ('Relaciones', {
            'fields': ('caja_id', 'usuario_id', 'cliente_id', 'empresa_id')
        }),
    )

    def fecha_venta_formateada(self, obj):
        return obj.fecha_venta.strftime("%d/%m/%Y %H:%M")
    fecha_venta_formateada.short_description = 'Fecha Venta'
    fecha_venta_formateada.admin_order_field = 'fecha_venta'

    def cliente_info(self, obj):
        if obj.cliente_id:
            return f"{obj.cliente_id.nombres} {obj.cliente_id.ap_paterno} ({obj.cliente_id.rut})"
        return "Sin cliente"
    cliente_info.short_description = 'Cliente'
    cliente_info.admin_order_field = 'cliente_id__nombres'

    def empresa_info(self, obj):
        if obj.empresa_id:
            return f"{obj.empresa_id.nombre_empresa} ({obj.empresa_id.rut_empresa})"
        return "Sin empresa"
    empresa_info.short_description = 'Empresa'
    empresa_info.admin_order_field = 'empresa_id__nombre_empresa'

    def caja_info(self, obj):
        if obj.caja_id:
            return f"{obj.caja_id.numero_caja} - {obj.caja_id.nombre_caja}"
        return "Sin caja"
    caja_info.short_description = 'Caja'
    caja_info.admin_order_field = 'caja_id__numero_caja'

    def usuario_info(self, obj):
        if obj.usuario_id:
            return f"{obj.usuario_id.get_full_name()} ({obj.usuario_id.username})"
        return "Sin usuario"
    usuario_info.short_description = 'Usuario'
    usuario_info.admin_order_field = 'usuario_id__username'

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ventas.csv"'
        response.write('\ufeff')  # BOM para UTF-8

        writer = csv.writer(response)
        writer.writerow([
            'ID Venta', 'Fecha Venta', 'Total Neto', 'Total IVA', 
            'Total Venta', 'Total Descuento', 'Estado', 'Caja', 
            'Usuario', 'Cliente', 'Empresa'
        ])

        for venta in queryset:
            writer.writerow([
                venta.id,
                venta.fecha_venta.strftime("%d/%m/%Y %H:%M"),
                venta.total_neto,
                venta.total_iva,
                venta.total_venta,
                venta.total_descuento,
                'Activa' if venta.estado else 'Anulada',
                f"{venta.caja_id.numero_caja} - {venta.caja_id.nombre_caja}" if venta.caja_id else '',
                f"{venta.usuario_id.get_full_name()} ({venta.usuario_id.username})" if venta.usuario_id else '',
                f"{venta.cliente_id.nombres} {venta.cliente_id.ap_paterno} ({venta.cliente_id.rut})" if venta.cliente_id else '',
                f"{venta.empresa_id.nombre_empresa} ({venta.empresa_id.rut_empresa})" if venta.empresa_id else ''
            ])

        return response
    export_to_csv.short_description = "Exportar seleccionados a CSV"

    def activar_ventas(self, request, queryset):
        updated = queryset.update(estado=True)
        self.message_user(
            request, 
            f"{updated} venta(s) marcada(s) como activa(s)."
        )
    activar_ventas.short_description = "Activar ventas seleccionadas"

    def anular_ventas(self, request, queryset):
        updated = queryset.update(estado=False)
        self.message_user(
            request, 
            f"{updated} venta(s) marcada(s) como anulada(s)."
        )
    anular_ventas.short_description = "Anular ventas seleccionadas"

    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related(
            'caja_id', 
            'usuario_id',
            'cliente_id',
            'empresa_id'
        )


# ==================== ITEM VENTA ====================
class ItemVentaInline(admin.TabularInline):
    model = ItemVenta
    extra = 0
    readonly_fields = ('total_item',)
    autocomplete_fields = ('producto_id',)


@admin.register(ItemVenta)
class ItemVentaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'venta_info', 'producto_info', 'cantidad', 
        'precio_unitario', 'descuento', 'total_item'
    )
    list_filter = ('producto_id__categoria_id', 'tipo_impuesto')
    search_fields = (
        'venta_id__id', 'producto_id__nombre', 'producto_id__codigo'
    )
    ordering = ('-venta_id__fecha_venta', 'id')
    actions = ['export_to_csv']
    raw_id_fields = ('venta_id', 'producto_id')
    autocomplete_fields = ('venta_id', 'producto_id')
    
    fieldsets = (
        ('Información del Ítem', {
            'fields': ('venta_id', 'producto_id', 'cantidad')
        }),
        ('Precios y Descuentos', {
            'fields': ('precio_unitario', 'descuento', 'total_item')
        }),
        ('Impuestos', {
            'fields': ('tipo_impuesto', 'valor_impuesto')
        }),
    )

    def venta_info(self, obj):
        if obj.venta_id:
            return f"Venta #{obj.venta_id.id} - {obj.venta_id.fecha_venta.strftime('%d/%m/%Y')}"
        return "Sin venta"
    venta_info.short_description = 'Venta'
    venta_info.admin_order_field = 'venta_id__id'

    def producto_info(self, obj):
        if obj.producto_id:
            return f"{obj.producto_id.nombre} ({obj.producto_id.codigo})"
        return "Sin producto"
    producto_info.short_description = 'Producto'
    producto_info.admin_order_field = 'producto_id__nombre'

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="items_venta.csv"'
        response.write('\ufeff')  # BOM para UTF-8

        writer = csv.writer(response)
        writer.writerow([
            'ID Ítem', 'ID Venta', 'Fecha Venta', 'Producto', 'Código Producto',
            'Cantidad', 'Precio Unitario', 'Descuento', 'Tipo Impuesto',
            'Valor Impuesto', 'Total Ítem'
        ])

        for item in queryset:
            writer.writerow([
                item.id,
                item.venta_id.id if item.venta_id else '',
                item.venta_id.fecha_venta.strftime("%d/%m/%Y %H:%M") if item.venta_id else '',
                item.producto_id.nombre if item.producto_id else '',
                item.producto_id.codigo if item.producto_id else '',
                item.cantidad,
                item.precio_unitario,
                item.descuento,
                item.tipo_impuesto,
                item.valor_impuesto,
                item.total_item
            ])

        return response
    export_to_csv.short_description = "Exportar seleccionados a CSV"

    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related(
            'venta_id', 
            'producto_id'
        )


# ==================== DOCUMENTO TRIBUTARIO ELECTRÓNICO ====================
class ItemDocumentoInline(admin.TabularInline):
    model = ItemDocumento
    extra = 0
    readonly_fields = ('valor_impuesto',)
    autocomplete_fields = ('item_venta_id',)


@admin.register(DocumentoTributarioElectronico)
class DocumentoTributarioElectronicoAdmin(admin.ModelAdmin):
    list_display = (
        'folio', 'tipo_documento', 'fecha_emision_formateada', 
        'total_documento', 'medio_pago', 'venta_info', 'estado'
    )
    list_filter = ('tipo_documento', 'estado', 'fecha_emision')
    search_fields = (
        'folio', 'venta_id__id', 'track_id_SII',
        'venta_id__cliente_id__rut', 'venta_id__cliente_id__nombres'
    )
    list_editable = ('estado',)
    ordering = ('-fecha_emision',)
    actions = ['export_to_csv', 'activar_documentos', 'anular_documentos']
    raw_id_fields = ('venta_id', 'documento_referencia_id')
    autocomplete_fields = ('venta_id', 'documento_referencia_id')
    readonly_fields = ('fecha_emision', 'track_id_SII')
    inlines = [ItemDocumentoInline]
    
    fieldsets = (
        ('Información del Documento', {
            'fields': ('folio', 'tipo_documento', 'fecha_emision', 'track_id_SII')
        }),
        ('Totales', {
            'fields': ('total_neto', 'total_iva', 'total_documento')
        }),
        ('Pago y Estado', {
            'fields': ('medio_pago', 'estado', 'motivo_anulacion')
        }),
        ('Relaciones', {
            'fields': ('venta_id', 'documento_referencia_id')
        }),
    )

    def fecha_emision_formateada(self, obj):
        return obj.fecha_emision.strftime("%d/%m/%Y %H:%M")
    fecha_emision_formateada.short_description = 'Fecha Emisión'
    fecha_emision_formateada.admin_order_field = 'fecha_emision'

    def venta_info(self, obj):
        if obj.venta_id:
            return f"Venta #{obj.venta_id.id} - ${obj.venta_id.total_venta}"
        return "Sin venta"
    venta_info.short_description = 'Venta'
    venta_info.admin_order_field = 'venta_id__id'

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="documentos_tributarios.csv"'
        response.write('\ufeff')  # BOM para UTF-8

        writer = csv.writer(response)
        writer.writerow([
            'Folio', 'Tipo Documento', 'Fecha Emisión', 'Total Neto',
            'Total IVA', 'Total Documento', 'Medio Pago', 'Estado',
            'Track ID SII', 'ID Venta', 'Total Venta', 'Documento Referencia'
        ])

        for doc in queryset:
            writer.writerow([
                doc.folio,
                doc.tipo_documento,
                doc.fecha_emision.strftime("%d/%m/%Y %H:%M"),
                doc.total_neto,
                doc.total_iva,
                doc.total_documento,
                doc.medio_pago,
                'Emitido' if doc.estado else 'Anulado',
                doc.track_id_SII,
                doc.venta_id.id if doc.venta_id else '',
                doc.venta_id.total_venta if doc.venta_id else '',
                f"{doc.documento_referencia_id.tipo_documento} #{doc.documento_referencia_id.folio}" if doc.documento_referencia_id else ''
            ])

        return response
    export_to_csv.short_description = "Exportar seleccionados a CSV"

    def activar_documentos(self, request, queryset):
        updated = queryset.update(estado=True)
        self.message_user(
            request, 
            f"{updated} documento(s) marcado(s) como emitido(s)."
        )
    activar_documentos.short_description = "Marcar como emitidos"

    def anular_documentos(self, request, queryset):
        updated = queryset.update(estado=False)
        self.message_user(
            request, 
            f"{updated} documento(s) marcado(s) como anulado(s)."
        )
    anular_documentos.short_description = "Anular documentos seleccionados"

    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related(
            'venta_id', 
            'documento_referencia_id'
        )


# ==================== ITEM DOCUMENTO ====================
@admin.register(ItemDocumento)
class ItemDocumentoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'documento_info', 'descripcion_corta', 'cantidad', 
        'precio_unitario', 'descuento', 'valor_impuesto'
    )
    list_filter = ('tipo_impuesto',)
    search_fields = (
        'documento_id__folio', 'descripcion', 
        'item_venta_id__producto_id__nombre'
    )
    ordering = ('-documento_id__fecha_emision', 'id')
    actions = ['export_to_csv']
    raw_id_fields = ('item_venta_id', 'documento_id')
    autocomplete_fields = ('item_venta_id', 'documento_id')
    
    fieldsets = (
        ('Información del Ítem', {
            'fields': ('documento_id', 'item_venta_id', 'descripcion', 'cantidad')
        }),
        ('Precios y Descuentos', {
            'fields': ('precio_unitario', 'descuento')
        }),
        ('Impuestos', {
            'fields': ('tipo_impuesto', 'valor_impuesto')
        }),
    )

    def documento_info(self, obj):
        if obj.documento_id:
            return f"{obj.documento_id.tipo_documento} #{obj.documento_id.folio}"
        return "Sin documento"
    documento_info.short_description = 'Documento'
    documento_info.admin_order_field = 'documento_id__folio'

    def descripcion_corta(self, obj):
        if len(obj.descripcion) > 50:
            return f"{obj.descripcion[:50]}..."
        return obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    descripcion_corta.admin_order_field = 'descripcion'

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="items_documento.csv"'
        response.write('\ufeff')  # BOM para UTF-8

        writer = csv.writer(response)
        writer.writerow([
            'ID Ítem', 'Documento', 'Tipo Documento', 'Folio', 
            'Descripción', 'Cantidad', 'Precio Unitario', 'Descuento',
            'Tipo Impuesto', 'Valor Impuesto'
        ])

        for item in queryset:
            writer.writerow([
                item.id,
                f"{item.documento_id.tipo_documento} #{item.documento_id.folio}" if item.documento_id else '',
                item.documento_id.tipo_documento if item.documento_id else '',
                item.documento_id.folio if item.documento_id else '',
                item.descripcion,
                item.cantidad,
                item.precio_unitario,
                item.descuento,
                item.tipo_impuesto,
                item.valor_impuesto
            ])

        return response
    export_to_csv.short_description = "Exportar seleccionados a CSV"

    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related(
            'documento_id', 
            'item_venta_id'
        )