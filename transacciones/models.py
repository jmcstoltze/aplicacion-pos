from django.db import models

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
        default=False,
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


class Venta(models.Model):
    """
    Modelo que representa una venta realizada en una caja registradora.

    Cada venta está asociada a una caja específica y contiene detalles sobre
    el monto total, la fecha y hora de la venta, y el usuario que la realizó.

    Attributes:
        caja_id (Caja): Caja en la que se realizó la venta (obligatorio).
        usuario_id (Usuario): Usuario que realizó la venta (opcional).
        monto_total (Decimal): Monto total de la venta.
        fecha_hora (DateTime): Fecha y hora en que se realizó la venta. """
    
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total_neto = models.DecimalField(max_digits=10, decimal_places=2)
    total_iva = models.DecimalField(max_digits=10, decimal_places=2)
    total_venta = models.DecimalField(max_digits=10, decimal_places=2)
    total_dscto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estado = models.BooleanField(default=True)  # True=Activa, False=Anulada
    caja_id = models.ForeignKey(
        Caja, on_delete=models.PROTECT,
        verbose_name="Caja",
        help_text="Caja en la que se realizó la venta")
    usuario_id = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Usuario",
        help_text="Usuario que realizó la venta")
    cliente_id = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Cliente",
        help_text="Cliente asociado a la venta (opcional)")
    empresa_id = models.ForeignKey(
        Empresa, on_delete=models.SET_NULL, null = True, blank=True,
        verbose_name="Empresa",
        help_text="Empresa a la que pertenece la venta")


class ItemVenta(models.Model):
    """
    Modelo que representa un ítem o producto vendido en una venta específica.

    Cada ítem de venta está asociado a una venta y contiene detalles sobre
    el producto, la cantidad vendida, el precio unitario y el subtotal.

    Attributes:
        venta_id (Venta): Venta a la que pertenece este ítem (obligatorio).
        producto_id (Producto): Producto vendido (obligatorio).
        cantidad (Integer): Cantidad del producto vendido.
        precio_unitario (Decimal): Precio unitario del producto en el momento de la venta.
        subtotal (Decimal): Subtotal calculado como cantidad * precio_unitario.
    """
    
    AFECTO = 'Afecto'
    EXENTO = 'Exento'

    TIPO_IMPUESTO_CHOICES = [
        (AFECTO, 'Afecto'),
        (EXENTO, 'Exento'),
    ]

    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tipo_impuesto = models.CharField(max_length=80) # Afecto o Exento
    valor_impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_item = models.DecimalField(max_digits=10, decimal_places=2)
    producto_id = models.ForeignKey(
        Producto, on_delete=models.PROTECT,
        verbose_name="Producto",
        help_text="Producto vendido en este ítem")
    venta_id = models.ForeignKey(Producto,null=True, blank=True, on_delete=models.PROTECT,
        verbose_name="Venta",
        help_text="Venta a la que pertenece este ítem")


class DocTribElec(models.Model):
    """
    Modelo que representa un documento tributario electrónico asociado a una venta.

    Cada documento tributario electrónico está vinculado a una venta específica
    y contiene detalles sobre el tipo de documento, el número de autorización,
    la fecha de emisión y el estado del documento.

    Attributes:
        venta_id (Venta): Venta a la que está asociado este documento (obligatorio).
        tipo_documento (str): Tipo de documento tributario (ej: 'Factura', 'Boleta').
        numero_autorizacion (str): Número de autorización del documento.
        fecha_emision (DateTime): Fecha y hora en que se emitió el documento.
        estado (str): Estado del documento (ej: 'Emitido', 'Anulado').
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

    folio = models.IntegerField()
    fecha_emision = models.DateTimeField(auto_now_add=True)
    tipo_documento = models.CharField(max_length=80) # Factura, Boleta, NC, ND
    total_neto = models.DecimalField(max_digits=10, decimal_places=2)
    total_iva = models.DecimalField(max_digits=10, decimal_places=2)
    total_documento = models.DecimalField(max_digits=10, decimal_places=2)
    medio_pago = models.CharField(
        max_length=250, null=False, blank=False,
        verbose_name="Medio de pago",
        help_text="Medio de pago que se emplea para cancelar el documento")
    estado = models.BooleanField(default=True) # Emitido - Anulado
    motivo_anulacion = models.CharField(
        max_length=250, null=True, blank=True,
        verbose_name="Motivo anulación",
        help_text="Motivo de la anulación del documento")
    venta_id = models.OneToOneField(Venta, null=False, blank=False, on_delete=models.PROTECT)
    documento_referencia_id = models.OneToOneField(
        'self', on_delete=models.PROTECT, null=True, blank=True)
    track_id_SII = models.IntegerField(null=False, blank=False)


class ItemDocumento(models.Model):
    """
    Modelo que representa un ítem o producto detallado en un documento tributario electrónico.

    Cada ítem de documento está asociado a un documento tributario electrónico
    y contiene detalles sobre el producto, la cantidad, el precio unitario y el subtotal.

    Attributes:
        doc_trib_elec_id (DocTribElec): Documento tributario electrónico al que pertenece este ítem (obligatorio).
        producto_id (Producto): Producto detallado en el documento (obligatorio).
        cantidad (Integer): Cantidad del producto en el documento.
        precio_unitario (Decimal): Precio unitario del producto en el documento.
        subtotal (Decimal): Subtotal calculado como cantidad * precio_unitario.
    """

    AFECTO = 'Afecto'
    EXENTO = 'Exento'

    TIPO_IMPUESTO_CHOICES = [
        (AFECTO, 'Afecto'),
        (EXENTO, 'Exento'),
    ]

    descripcion = models.CharField(max_length=250, null=False, blank=False)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tipo_impuesto = models.CharField(max_length=80) # Afecto, exento
    valor_impuesto = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    item_venta_id = models.ForeignKey(ItemVenta, on_delete=models.PROTECT, null=True, blank=True)
    documento_id = models.Foreign(DocTribElec, on_delete=models.PROTECT, null=False, blank=False)


