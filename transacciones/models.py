from django.db import models
from django.core.validators import MinValueValidator

from comercio.models import Sucursal, Producto
from usuarios.models import Usuario
from clientes.models import Cliente, Empresa

# Representa a las caja asociadas a cada sucursal y a un usuario
class Caja(models.Model):
    """
    Modelo que representa una caja registradora o punto de venta en una sucursal.

    Cada caja está asociada a una sucursal específica y puede tener un usuario asignado.
    Se utiliza para gestionar transacciones de venta y operaciones de cobro.

    Attributes:
        numero_caja (str): Identificador único o número de la caja (ej: 'CAJ001').
        nombre_caja (str): Nombre descriptivo de la caja (ej: 'Caja Principal').
        estado (bool): Estado operativo (True=Activa, False=Inactiva).
        esta_asignada (bool): Indica si la caja tiene un usuario asignado actualmente.
        usuario_id (Usuario): Usuario asignado a la caja (opcional).
        sucursal_id (Sucursal): Sucursal a la que pertenece la caja (obligatorio).

    Methods:
        __str__: Representación legible que incluye número, nombre y sucursal.
    """
    numero_caja = models.CharField(
        max_length=60, null=False, blank=False,
        verbose_name="Número de caja",
        help_text="Identificador único o número de la caja (ej: 'CAJ001')")
    
    nombre_caja = models.CharField(
        max_length=80, null=False, blank=False,
        verbose_name="Nombre de la caja",
        help_text="Nombre descriptivo de la caja (ej: 'Caja Principal')")
    
    estado = models.BooleanField(
        default=True,
        verbose_name="Activa",
        help_text="Indica si la caja está operativa")
    
    esta_asignada = models.BooleanField(
        default=False,
        verbose_name="Asignada",
        help_text="Indica si la caja tiene un usuario asignado actualmente")
    
    usuario_id = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, # Si se elimina el usuario, la relación es NULL
        verbose_name="Usuario asignado",
        help_text="Usuario actualmente asignado a esta caja")
    
    sucursal_id = models.ForeignKey(
        Sucursal, on_delete=models.PROTECT, # Eliminación protegida
        verbose_name="Sucursal",
        help_text="Sucursal a la que pertenece esta caja")
    
    def __str__(self):
        """
        Representación legible de la caja incluyendo número, nombre y sucursal.
        Ejemplo: "CAJ001 - Caja Principal [Sucursal Centro]"
        """
        estado_str = " (Activa)" if self.estado else " (Inactiva)"
        asignada_str = " - Asignada" if self.esta_asignada else ""
        sucursal_str = f" [{self.sucursal_id.nombre_sucursal}]" if self.sucursal_id else " [Sin sucursal]"
        return f"{self.numero_caja} - {self.nombre_caja}{estado_str}{asignada_str}{sucursal_str}"
    
    class Meta:
        verbose_name = "Caja registradora"
        verbose_name_plural = "Cajas registradoras"
        ordering = ['sucursal_id__nombre_sucursal', 'numero_caja']
        indexes = [
            models.Index(fields=['sucursal_id', 'numero_caja']),
            models.Index(fields=['estado', 'esta_asignada']),
        ]

# Representa una venta realizada en una caja registradora
class Venta(models.Model):
    """
    Modelo que representa una venta realizada en una caja registradora.

    Cada venta está asociada a una caja específica y contiene detalles sobre
    el monto total, la fecha y hora de la venta, y el usuario que la realizó.

    Attributes:
        fecha_venta (DateTime): Fecha y hora en que se realizó la venta (auto-generada).
        total_neto (Decimal): Monto neto de la venta antes de impuestos.
        total_iva (Decimal): Monto del IVA aplicado a la venta.
        total_venta (Decimal): Monto total de la venta incluyendo impuestos.
        total_descuento (Decimal): Monto total de descuentos aplicados (por defecto 0.00).
        estado (bool): Estado de la venta (True=Activa, False=Anulada).
        caja_id (Caja): Caja en la que se realizó la venta (obligatorio).
        usuario_id (Usuario): Usuario que realizó la venta.
        cliente_id (Cliente): Cliente asociado a la venta (opcional).
        empresa_id (Empresa): Empresa a la que pertenece la venta (opcional).
    """
    
    fecha_venta = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de venta",
        help_text="Fecha y hora en que se realizó la venta")
    
    total_neto = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Total neto",
        help_text="Monto neto de la venta antes de impuestos",
        validators=[MinValueValidator(0.00)])
    
    total_iva = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Total IVA",
        help_text="Monto del IVA aplicado a la venta",
        validators=[MinValueValidator(0.00)])
    
    total_venta = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Total venta",
        help_text="Monto total de la venta incluyendo impuestos",
        validators=[MinValueValidator(0.00)])
    
    total_descuento = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Total descuento",
        help_text="Monto total de descuentos aplicados",
        validators=[MinValueValidator(0.00)])
    
    estado = models.BooleanField(
        default=True,
        verbose_name="Estado",
        help_text="True=Venta activa, False=Venta anulada")  # True=Activa, False=Anulada
    
    caja_id = models.ForeignKey(
        Caja, on_delete=models.PROTECT,
        verbose_name="Caja",
        help_text="Caja en la que se realizó la venta")
    
    usuario_id = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, null=False, blank=False,
        verbose_name="Usuario",
        help_text="Usuario que realizó la venta")
    
    cliente_id = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Cliente",
        help_text="Cliente asociado a la venta (opcional)")
    
    empresa_id = models.ForeignKey(
        Empresa, on_delete=models.SET_NULL, null = True, blank=True,
        verbose_name="Empresa",
        help_text="Empresa a la que pertenece la venta(opcional)")
    
    def __str__(self):
        """Representación legible de la venta con ID, fecha y total."""
        return f"Venta #{self.id} - {self.fecha_venta.strftime('%Y-%m-%d %H:%M')} - ${self.total_venta}"

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_venta']
        indexes = [
            models.Index(fields=['fecha_venta']),
            models.Index(fields=['caja_id', 'fecha_venta']),
            models.Index(fields=['cliente_id', 'fecha_venta']),
        ]

# Representa un ítem o producto vendido en una venta
class ItemVenta(models.Model):
    """
    Modelo que representa un ítem o producto vendido en una venta específica.

    Cada ítem de venta está asociado a una venta y contiene detalles sobre
    el producto, la cantidad vendida, el precio unitario y el subtotal.

    Attributes:
        venta_id (Venta): Venta a la que pertenece este ítem.
        producto_id (Producto): Producto vendido.
        cantidad (Integer): Cantidad del producto vendido.
        precio_unitario (Decimal): Precio unitario del producto.
        descuento (Decimal): Descuento aplicado al ítem.
        tipo_impuesto (str): Tipo de impuesto (Afecto/Exento).
        valor_impuesto (Decimal): Valor del impuesto aplicado.
        total_item (Decimal): Total del ítem (cantidad * precio - descuento + impuesto).
    """
    
    AFECTO = 'Afecto'
    EXENTO = 'Exento'

    TIPO_IMPUESTO_CHOICES = [
        (AFECTO, 'Afecto'),
        (EXENTO, 'Exento'),
    ]

    cantidad = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad",
        help_text="Cantidad del producto vendido")
    
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Precio unitario",
        help_text="Precio unitario del producto",
        validators=[MinValueValidator(0.00)])
    
    descuento = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Descuento",
        help_text="Descuento aplicado al ítem",
        validators=[MinValueValidator(0.00)])
    
    tipo_impuesto = models.CharField(
        max_length=80, choices=TIPO_IMPUESTO_CHOICES,
        verbose_name="Tipo de impuesto",
        help_text="Indica se el producto está afecto o exento de impuestos") # Afecto o Exento
    
    valor_impuesto = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Valor del impuesto",
        help_text="Valor del impuesto aplicado al ítem",
        validators=[MinValueValidator(0.00)])
    
    total_item = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Total ítem",
        help_text="Total del ítem (cantidad * precio - descuento + impuesto)",
        validators=[MinValueValidator(0.00)])
    
    producto_id = models.ForeignKey(
        Producto, on_delete=models.PROTECT,
        verbose_name="Producto",
        help_text="Producto vendido en este ítem")
    
    venta_id = models.ForeignKey(
        Producto, on_delete=models.PROTECT, null=True, blank=True,
        verbose_name="Venta",
        help_text="Venta a la que pertenece este ítem",
        related_name="items")
    
    def __str__(self):
        """Representación legible del ítem de venta."""
        return f"Ítem #{self.id} - {self.producto_id.nombre if self.producto_id else 'Producto'} x{self.cantidad}"
    
    class Meta:
        verbose_name = "Ítem de venta"
        verbose_name_plural = "Ítems de venta"
        ordering = ['venta_id', 'id']
        indexes = [
            models.Index(fields=['venta_id']),
            models.Index(fields=['producto_id']),
        ]

# Representa un documento tributario electrónico asociado a una venta
class DocumentoTributarioElectronico(models.Model):
    """
    Modelo que representa un documento tributario electrónico asociado a una venta.

    Cada documento tributario electrónico está vinculado a una venta específica
    y contiene detalles sobre el tipo de documento, el número de autorización,
    la fecha de emisión y el estado del documento.

    Attributes:
        folio (int): Número de folio del documento.
        fecha_emision (DateTime): Fecha y hora de emisión del documento.
        tipo_documento (str): Tipo de documento tributario.
        total_neto (Decimal): Monto neto del documento.
        total_iva (Decimal): Monto total de IVA.
        total_documento (Decimal): Monto total del documento.
        medio_pago (str): Medio de pago utilizado.
        estado (bool): Estado del documento (True=Emitido, False=Anulado).
        motivo_anulacion (str): Motivo de anulación (opcional).
        venta_id (Venta): Venta asociada al documento.
        documento_referencia_id (DocumentoTributarioElectronico): Documento de referencia (para NC/ND).
        track_id_SII (int): ID de tracking del SII.
    """

    FACTURA = 'Factura'
    BOLETA = 'Boleta'
    NC = 'Nota de Crédito'
    ND = 'Nota de Débito'

    TIPO_DOCUMENTO_CHOICES = [
        (FACTURA, 'Factura'),
        (BOLETA, 'Boleta'),
        (NC, 'Nota de Crédito'),
        (ND, 'Nota de Débito'),
    ]

    folio = models.IntegerField(
        verbose_name="Folio",
        help_text="Número de folio del documento")
    
    fecha_emision = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de emisión",
        help_text="Fecha y hora en que se emitió el documento")
    
    tipo_documento = models.CharField(
        max_length=80, choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name="Tipo de documento",
        help_text="Tipo de documento tributario") # Factura, Boleta, NC, ND
    
    total_neto = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Total neto",
        help_text="Monto neto del documento",
        validators=[MinValueValidator(0.00)])
    
    total_iva = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Total IVA",
        help_text="Monto total de IVA",
        validators=[MinValueValidator(0.00)])
    
    total_documento = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Total documento",
        help_text="Monto total del documento",
        validators=[MinValueValidator(0.00)])
    
    medio_pago = models.CharField(
        max_length=250, null=False, blank=False,
        verbose_name="Medio de pago",
        help_text="Medio de pago que se emplea para cancelar el documento")
    
    estado = models.BooleanField(
        default=True,
        verbose_name="Estado",
        help_text="True=Documento emitido, False=Documento anulado") # Emitido - Anulado
    
    motivo_anulacion = models.CharField(
        max_length=250, null=True, blank=True,
        verbose_name="Motivo anulación",
        help_text="Motivo de la anulación del documento")
    
    venta_id = models.OneToOneField(
        Venta, on_delete=models.PROTECT,
        verbose_name="Venta",
        help_text="Venta asociada a este documento")
    
    documento_referencia_id = models.OneToOneField(
        'self', on_delete=models.PROTECT, null=True, blank=True,
        verbose_name="Documento de referencia",
        help_text="Documento de referencia (para NC/ND)")
    
    track_id_SII = models.IntegerField(
        null=False, blank=False,
        verbose_name="Track ID SII",
        help_text="ID de tracking asignado por el SII")
    
    def __str__(self):
        """Representación legible del documento tributario."""
        estado_str = "Emitido" if self.estado else "Anulado"
        return f"{self.tipo_documento} #{self.folio} - {estado_str} - ${self.total_documento}"
    
    class Meta:
        verbose_name = "Documento tributario electrónico"
        verbose_name_plural = "Documentos tributarios electrónicos"
        ordering = ['-fecha_emision']
        indexes = [
            models.Index(fields=['folio', 'tipo_documento']),
            models.Index(fields=['fecha_emision']),
            models.Index(fields=['track_id_SII']),
        ]
        unique_together = [['folio', 'tipo_documento']]

# Representa un ítem o producto detallado en un documento tributario electrónico
class ItemDocumento(models.Model):
    """
    Modelo que representa un ítem o producto detallado en un documento tributario electrónico.

    Cada ítem de documento está asociado a un documento tributario electrónico
    y contiene detalles sobre el producto, la cantidad, el precio unitario y el subtotal.

    Attributes:
        descripcion (str): Descripción del ítem.
        cantidad (int): Cantidad del producto.
        precio_unitario (Decimal): Precio unitario del producto.
        descuento (Decimal): Descuento aplicado al ítem.
        tipo_impuesto (str): Tipo de impuesto (Afecto/Exento).
        valor_impuesto (Decimal): Valor del impuesto aplicado.
        item_venta_id (ItemVenta): Ítem de venta asociado.
        documento_id (DocTribElec): Documento tributario al que pertenece.
    """

    AFECTO = 'Afecto'
    EXENTO = 'Exento'

    TIPO_IMPUESTO_CHOICES = [
        (AFECTO, 'Afecto'),
        (EXENTO, 'Exento'),
    ]

    descripcion = models.CharField(
        max_length=250, null=False, blank=False,
        verbose_name="Descripción",
        help_text="Descripción del ítem en el documento")
    
    cantidad = models.IntegerField(
        verbose_name="Cantidad",
        help_text="Cantidad del producto",
        validators=[MinValueValidator(1)])
    
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False,
        verbose_name="Precio unitario",
        help_text="Precio unitario del producto",
        validators=[MinValueValidator(0.00)])
    
    descuento = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Descuento",
        help_text="Descuento aplicado al ítem",
        validators=[MinValueValidator(0.00)])
    
    tipo_impuesto = models.CharField(
        max_length=80, choices=TIPO_IMPUESTO_CHOICES,
        verbose_name="Tipo de impuesto",
        help_text="Indica si el ítem está afecto o exento de impuestos") # Afecto, exento
    
    valor_impuesto = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False,
        verbose_name="Valor del impuesto",
        help_text="Valor del impuesto aplicado al ítem",
        validators=[MinValueValidator(0.00)])
    
    item_venta_id = models.ForeignKey(
        ItemVenta, on_delete=models.PROTECT, null=True, blank=True,
        verbose_name="Ítem de venta",
        help_text="Ítem de venta asociado a este ítem del documento")
    
    documento_id = models.ForeignKey(
        DocumentoTributarioElectronico, on_delete=models.PROTECT, null=False, blank=False,
        verbose_name="Documento",
        help_text="Documento tributario al que pertenece este ítem",
        related_name="items")
    
    def __str__(self):
        """Representación legible del ítem de documento."""
        return f"Ítem Doc #{self.id} - {self.descripcion[:50]}"
    
    class Meta:
        verbose_name = "Ítem de documento"
        verbose_name_plural = "Ítems de documento"
        ordering = ['documento_id', 'id']
        indexes = [
            models.Index(fields=['documento_id']),
        ]
