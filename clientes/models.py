from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator

from usuarios.models import Comuna

# Validadores personalizados
rut_validator = RegexValidator(
    regex=r'^\d{7,8}-[\dkK]$',
    message='El RUT debe estar en formato 12345678-9'
)
telefono_validator = RegexValidator(
    regex=r'^\+?56?[2-9]\d{8}$',
    message='El teléfono debe ser válido (ej: +56912345678 o 912345678)'
)

# Representa a un cliente del comercio
class Cliente(models.Model):
    """
    Modelo que representa a un cliente del comercio en el sistema POS.

    Almacena información personal, de contacto y ubicación de los clientes
    para gestión comercial, facturación y marketing.

    Attributes:
        rut (CharField): Rol Único Tributario (formato: XXXXXXXX-X)
        nombres (CharField): Nombres del cliente
        ap_paterno (CharField): Apellido paterno
        ap_materno (CharField): Apellido materno
        telefono (CharField): Teléfono de contacto
        email (EmailField): Correo electrónico
        direccion (CharField): Dirección física
        estado (BooleanField): Estado activo/inactivo del cliente
        comuna_id (ForeignKey): Comuna de residencia
        fecha_creacion (DateTimeField): Fecha de creación del registro
        fecha_actualizacion (DateTimeField): Fecha de última actualización

    Methods:
        __str__: Representación legible
        nombre_completo: Propiedad que devuelve el nombre completo
        es_activo: Propiedad que verifica si el cliente está activo

    Meta:
        Configuración de metadatos para la interfaz administrativa
    """
    
    rut = models.CharField(
        max_length=12,
        null=False,
        blank=False,
        unique=True,
        help_text="RUT en formato 12345678-9 (sin puntos, con guión y dígito verificador)"
    )
    
    nombres = models.CharField(
        max_length=80,
        null=False,
        blank=False,
        verbose_name="Nombres",
        help_text="Nombres del cliente (ej: Juan Carlos)"
    )
    
    ap_paterno = models.CharField(
        max_length=80,
        null=False,
        blank=False,
        verbose_name="Apellido Paterno",
        help_text="Apellido paterno (ej: González)"
    )
    
    ap_materno = models.CharField(
        max_length=80,
        null=False,
        blank=False,
        verbose_name="Apellido Materno",
        help_text="Apellido materno (ej: Pérez)"
    )

    telefono = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        validators=[telefono_validator],
        verbose_name="Teléfono",
        help_text="Teléfono de contacto (+56912345678 o 912345678)"
    )

    email = models.EmailField(
        max_length=80,
        null=False,
        blank=False,
        verbose_name="Correo Electrónico",
        help_text="Correo electrónico válido (ej: cliente@dominio.com)")
    
    direccion = models.CharField(
        max_length=250,
        null=False,
        blank=False,
        verbose_name="Dirección",
        help_text="Dirección completa (calle, número, depto, etc.)")
    
    estado = models.BooleanField(
        default=True,
        verbose_name="Estado Activo",
        help_text="Indica si el cliente está activo en el sistema"
    )

    comuna_id = models.ForeignKey(
        Comuna,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Comuna",
        help_text="Comuna de residencia del cliente"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación",
        help_text="Fecha y hora en que se creó el registro"
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización",
        help_text="Fecha y hora de la última actualización del registro"
    )
    
    def __str__(self):
        """Representación legible para selects/admin."""
        return f"{self.ap_paterno} {self.ap_materno}, {self.nombres} ({self.rut})"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['ap_paterno', 'ap_materno', 'nombres']
        indexes = [
            models.Index(fields=['rut']),
            models.Index(fields=['ap_paterno', 'ap_materno']),
            models.Index(fields=['estado']),
            models.Index(fields=['comuna_id']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['rut'],
                name='unique_cliente_rut'
            ),
        ]

# Representa a una empresa cliente que compra en el comercio
class Empresa(models.Model):
    """
    Modelo que representa una empresa cliente que realiza compras en el comercio.

    Registra información legal y comercial de empresas que son clientes del negocio,
    incluyendo sus datos tributarios, representante legal y ubicación geográfica.

    Attributes:
        nombre_empresa (CharField): Nombre comercial o de fantasía
        razon_social (CharField): Nombre legal registrado
        giro (CharField): Actividad económica principal
        rut_empresa (CharField): RUT de la empresa
        direccion (CharField): Dirección fiscal
        telefono (CharField): Teléfono de contacto
        email (EmailField): Correo electrónico
        representante_id (ForeignKey): Representante legal
        comuna_id (ForeignKey): Comuna de ubicación
        estado (BooleanField): Estado activo/inactivo
        fecha_creacion (DateTimeField): Fecha de creación
        fecha_actualizacion (DateTimeField): Fecha de actualización

    Methods:
        __str__: Representación legible
        info_completa: Propiedad con información completa

    Meta:
        Configuración de metadatos para la interfaz administrativa
    """

    nombre_empresa = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        verbose_name="Nombre de la Empresa",
        help_text="Nombre de fantasía o marca (ej: 'Tech Solutions')"
    )
    
    razon_social = models.CharField(
        max_length=250,
        null=False,
        blank=False,
        unique=True,
        help_text="Nombre legal registrado (ej: 'TECH SOLUTIONS S.A.')"
    )

    giro = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        verbose_name="Giro Comercial",
        help_text="Actividad económica principal (ej: 'VENTA EQUIPOS TECNOLÓGICOS')"
    )

    rut_empresa = models.CharField(
        max_length=12,
        null=False,
        blank=False,
        unique=True,
        validators=[rut_validator],
        verbose_name="RUT de la Empresa",
        help_text="RUT en formato 12345678-9 (sin puntos, con guión y dígito verificador)"
    )

    direccion = models.CharField(
        max_length=250,
        null=False,
        blank=False,
        verbose_name="Dirección",
        help_text="Dirección fiscal completa (calle, número, depto, etc.)"
    )

    telefono = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        validators=[telefono_validator],
        verbose_name="Teléfono",
        help_text="Teléfono de contacto (+56912345678 o 912345678)"
    )

    email = models.EmailField(
        max_length=80,
        null=False,
        blank=False,
        verbose_name="Correo Electrónico",
        help_text="Correo electrónico válido de la empresa"
    )
        
    representante_id = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT, # Eliminación protegida
        verbose_name="Representante Legal",
        help_text="Cliente registrado como representante legal"
    )

    comuna_id = models.ForeignKey(
        Comuna,
        on_delete=models.PROTECT, # Eliminación protegida
        verbose_name="Comuna",
        help_text="Comuna de la empresa"
    )

    estado = models.BooleanField(
        default=True,
        verbose_name="Estado Activo",
        help_text="Indica si la empresa está activa en el sistema"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación",
        help_text="Fecha y hora en que se creó el registro"
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización",
        help_text="Fecha y hora de la última actualización del registro"
    )     
    
    def __str__(self):
        """Representación legible para selects/admin."""
        return f"{self.nombre_empresa} - {self.razon_social}"

    class Meta:
        verbose_name = "Empresa Cliente"
        verbose_name_plural = "Empresas Clientes"
        ordering = ['nombre_empresa']
        indexes = [
            models.Index(fields=['razon_social']),
            models.Index(fields=['rut_empresa']),
            models.Index(fields=['nombre_empresa']),
            models.Index(fields=['estado']),
            models.Index(fields=['comuna_id']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['razon_social'],
                name='unique_empresa_razon_social'
            ),
            models.UniqueConstraint(
                fields=['rut_empresa'],
                name='unique_empresa_rut'
            ),
        ]
