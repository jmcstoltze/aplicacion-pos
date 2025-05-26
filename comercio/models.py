from django.db import models

from usuarios.models import Comuna

class Comercio(models.Model):
    """
    Modelo que representa un Comercio o establecimiento comercial en el sistema.

    Almacena información básica del comercio incluyendo sus datos de contacto
    y denominaciones legales. Se utiliza para gestionar la relación con clientes,
    proveedores o transacciones.

    Attributes:
        nombre_comercio (CharField): Nombre de fantasía o público del comercio.
        razon_social (CharField): Nombre legal registrado (debe ser único en el sistema).
        email (EmailField): Correo electrónico corporativo válido.
        telefono (CharField): Número de contacto en formato internacional.

    Methods:
        __str__: Representación legible del comercio (devuelve nombre_comercio + razón social).

    Meta:
        verbose_name: Nombre singular para la interfaz administrativa.
        verbose_name_plural: Nombre plural para la interfaz administrativa.
        ordering: Ordenamiento por defecto (nombre_comercio ascendente).
        indexes: Índice para mejorar búsquedas por razón social.
        constraints: Restricción de unicidad para email corporativo.
    """

    nombre_comercio = models.CharField(
        max_length=160, null=False, blank=False,
        help_text="Nombre de fantasía del comercio")
    razon_social = models.CharField(
        max_length=250, null=False, blank=False, unique=True,
        help_text="Razón social o nombre legal del comercio")
    email = models.EmailField(
        max_length=80, null=False, blank=False,
        help_text="Correo electrónico válido corporativo para el comercio")
    telefono = models.CharField(
        max_length=20, null=False, blank=False,
        help_text="Número de contacto en formato +56912345678")

    def __str__(self):
        """Representación legible."""
        return f"{self.nombre_comercio} | {self.razon_social}"

    class Meta:
        verbose_name = "Comercio"
        verbose_name_plural = "Comercios"
        ordering = ["nombre_comercio"]
   
class Sucursal(models.Model):
    """
    Modelo que representa una sucursal física perteneciente a un Comercio.

    Cada sucursal tiene información de contacto, ubicación geográfica y estados operativos.
    Se relaciona con un Comercio principal y una Comuna específica.

    Attributes:
        nombre_sucursal (CharField): Nombre identificatorio único de la sucursal (80 chars).
        email (EmailField): Correo electrónico corporativo válido.
        telefono (CharField): Teléfono en formato internacional (+56912345678).
        es_casa_matriz (BooleanField): Indica si es la sede principal del comercio.
        esta_asignada (BooleanField): Indica si la sucursal tiene asignación operativa.
        estado (BooleanField): Estado activo/inactivo de la sucursal.
        comercio (ForeignKey): Relación con el Comercio al que pertenece.
        comuna (ForeignKey): Ubicación geográfica referencial.

    Methods:
        __str__: Representación legible en formato: [CASA MATRIZ] Nombre (Comercio).

    Meta:
        verbose_name: Configuración para la interfaz administrativa.
        ordering: Ordenamiento predeterminado de registros.
    """

    nombre_sucursal = models.CharField(
        max_length=80, null=False, blank=False, unique=True,
        help_text="Nombre referencial o identificatorio de la sucursal ")
    email = models.EmailField(
        max_length=80, null=False, blank=False,
        help_text="Correo electrónico válido corporativo para la sucursal")
    telefono = models.CharField(
        max_length=20, null=False, blank=False,
        help_text="Número de contacto en formato +56912345678")
    es_casa_matriz = models.BooleanField(
        default=False, # No casa matriz por defecto
        verbose_name = "Casa Matriz",
        help_text="Indica si la sucursal es casa matriz o no")
    esta_asignada = models.BooleanField(
        default=False, # No asignada por defecto
        verbose_name = "Asignada",
        help_text="Indica si la sucursal está asignada o no")
    estado = models.BooleanField(
        default=True, # Activa por defecto
        verbose_name = "Activa",
        help_text="Indica si la sucursal está activa o no")
    comercio_id = models.ForeignKey(
        Comercio, on_delete=models.PROTECT, # Eliminación protegida
        help_text="Comercio que lidera el conjunto de sucursales",
        related_name="comercio")
    comuna = models.ForeignKey(
        Comuna, on_delete=models.PROTECT, # Eliminación protegida
        help_text="Comuna de la dirección de la sucursal",
        related_name="comuna")
    
    def __str__(self):
        """Representación legible que incluye estado de casa matriz."""
        matriz_flag = "[CASA MATRIZ] " if self.es_casa_matriz else ""
        return f"{matriz_flag}{self.nombre_sucursal}"

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"
        ordering = ["-es_casa_matriz", "nombre_sucursal"]  # Casa matriz primero

class Bodega(models.Model):
    pass