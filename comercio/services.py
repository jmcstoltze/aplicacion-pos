from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction, models
from .models import Producto

def crear_producto(
        sku,
        codigo_barra,
        nombre_producto,
        nombre_abreviado,
        descripcion,
        precio_venta=None,
        **kwargs
):
    """
    Crea un nuevo producto en el sistema con validaciones.
    
    Args:
        sku (str): Código único del producto
        codigo_barra (str): Código de barras
        nombre_producto (str): Nombre completo
        nombre_abreviado (str): Nombre abreviado
        descripcion (str): Descripción detallada
        precio_venta (Decimal): Precio (opcional)
        **kwargs: Otros campos del modelo
        
    Returns:
        Producto: El producto creado
        
    Raises:
        ValidationError: Si hay errores en los datos
        Exception: Para errores inesperados
    """
    try:
        with transaction.atomic():
            # Validar campos requeridos
            if not all([sku, codigo_barra, nombre_producto, nombre_abreviado, descripcion]):
                raise ValidationError("Todos los campos obligatorios deben ser proporcionados")
            
            # Validar unicidad de campos únicos
            #########################################

            if Producto.objects.filter(sku=sku).exists():
                raise ValidationError(f"El SKU {sku} ya existe")
            
            if Producto.objects.filter(codigo_barra=codigo_barra).exists():
                raise ValidationError(f"El código de barras {codigo_barra} ya existe")

            if Producto.objects.filter(nombre_producto=nombre_producto).exists():
                raise ValidationError(f"El nombre de producto {nombre_producto} ya existe")
                
            if Producto.objects.filter(nombre_abreviado=nombre_abreviado).exists():
                raise ValidationError(f"El nombre abreviado {nombre_abreviado} ya existe")
            
            # Valida precio si se proporciona
            if precio_venta is not None and precio_venta < 0:
                raise ValidationError("El precio de venta no puede ser negativo")
            
            # Crear el producto
            producto = Producto(
                sku=sku,
                codigo_barra=codigo_barra,
                nombre_producto=nombre_producto,
                nombre_abreviado=nombre_abreviado,
                descripcion=descripcion,
                precio_venta=precio_venta,
                **kwargs
            )

            # Validación completa del modelo
            producto.full_clean()

            # Guardar en la base de datos
            producto.save()

            return producto
    
    except ValidationError as ve:
        raise ValidationError(f"Error de validación: {str(ve)}")
    except Exception as e:
        raise Exception(f"Error inesperado al crear producto: {str(e)}")

def listar_productos(
        filtros=None,
        orden='nombre_producto',
        pagina=1,
        items_por_pagina=20,
        solo_disponibles=False
):
    """
    Obtiene una lista paginada de productos con opciones de filtrado y ordenamiento.
    
    Args:
        filtros (dict): Diccionario con campos para filtrar (opcional)
        orden (str): Campo por el que ordenar (default: nombre_producto)
        pagina (int): Número de página a mostrar (default: 1)
        items_por_pagina (int): Cantidad de items por página (default: 20)
        solo_disponibles (bool): Si True, solo muestra productos disponibles
        
    Returns:
        dict: {
            'productos': QuerySet de productos,
            'pagina_actual': int,
            'total_paginas': int,
            'total_productos': int
        }
        
    Raises:
        ValueError: Si los parámetros son inválidos
    """
    try:
        # Validar parámetros de orden
        campos_validos = [f.name for f in Producto._meta.get_fields()]
        if orden.lstrip('-') not in campos_validos:
            raise ValueError(f"Campo de ordenamiento inválido: {orden}")
        
        # Obtener todos los productos
        queryset =Producto.objects.all()

        # Filtrar por disponibilidad si se solicita
        if solo_disponibles:
            queryset = queryset.filter(disponible=True)

        # Aplicar filtros adicionales si existen
        if filtros:
            if not isinstance(filtros, dict):
                raise ValueError("Los filtros deben ser un diccionario")
            
            # Construir el filtro dinámicamente
            filtros_q = {}
            for campo, valor in filtros.items():
                if campo in campos_validos:
                    # Para búsquedas de texto parcial en campos CharField
                    if campo in ['nombre_producto', 'nombres_abreviado', 'descripcion', 'sku']:
                        filtros_q['f{campo}__icontains'] = valor
                    else:
                        filtros_q[campo] = valor

            queryset = queryset.filter(**filtros_q)

        # Ordenar los resultados
        queryset = queryset.order_by(orden)

        # Paginación
        paginator = Paginator(queryset, items_por_pagina)

        try:
            productos_paginados = paginator.page(pagina)
        except PageNotAnInteger:
            productos_paginados = paginator.page(1)
        except EmptyPage:
            productos_paginados = paginator.page(paginator.num_pages)

        return {
            'productos': productos_paginados,
            'pagina_actual': productos_paginados.number,
            'total_paginas': paginator.num_pages,
            'total_productos': paginator.count
        }
    
    except Exception as e:
        raise ValueError(f"Error al listar productos: {str(e)}")

def editar_producto(producto_id, **kwargs):
    """
    Edita un producto existente con los datos proporcionados.
    
    Args:
        producto_id: ID del producto a editar
        **kwargs: Campos a actualizar con sus nuevos valores
        
    Returns:
        Producto: El producto editado
        
    Raises:
        ObjectDoesNotExist: Si no se encuentra el producto
        ValidationError: Si los datos no son válidos
        Exception: Para otros errores inesperados
    """
    try:
        with transaction.atomic():
            producto = Producto.objects.get(pk=producto.id)

            # Campos que no deben ser editados directamente
            campos_protegidos = ['created_at', 'updated_at']
            for campo in campos_protegidos:
                if campo in kwargs:
                    del kwargs[campo]

            # Validar campos únicos antes de actualizar
            ##################################################

            if 'sku' in kwargs and kwargs['sku'] != producto.sku:
                if Producto.objects.filter(sku=kwargs['sku']).exclude(pk=producto_id).exists():

                    raise ValidationError(f"El SKU {kwargs['sku']} ya está en uso por otro producto")
                
            if 'codigo_barra' in kwargs and kwargs['codigo_barra'] != producto.codigo_barra:

                if Producto.objects.filter(codigo_barra=kwargs['codigo_barra']).exclude(pk=producto_id).exists():
                    raise ValidationError(f"El código de barras {kwargs['codigo_barra']} ya está en uso")
                
            if 'nombre_producto' in kwargs and kwargs['nombre_producto'] != producto.nombre_producto:

                if Producto.objects.filter(nombre_producto=kwargs['nombre_producto']).exclude(pk=producto_id).exists():
                    raise ValidationError(f"El nombre de producto {kwargs['nombre_producto']} ya está en uso")
            
            if 'nombre_abreviado' in kwargs and kwargs['nombre_abreviado'] != producto.nombre_abreviado:
                if Producto.objects.filter(nombre_abreviado=kwargs['nombre_abreviado']).exclude(pk=producto_id).exists():
                    raise ValidationError(f"El nombre abreviado {kwargs['nombre_abreviado']} ya está en uso")
                
            # Validar precio positivo si se está actualizando
            if 'precio_venta' in kwargs and kwargs['precio_venta'] is not None:
                if float(kwargs['precio_venta']) < 0:
                    raise ValidationError("El precio de venta no puede ser negativo")
            
            # Actualizar los campos
            for key, value in kwargs.items():
                setattr(producto, key, value)

            producto.save()
            return producto
    
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(f"No se encontró el producto con ID {producto_id}")
    except ValidationError as ve:
        raise ValidationError(f"Error de validación: {str(ve)}")
    except Exception as e:
        raise Exception(f"Error inesperado al editar producto: {str(e)}")

def eliminar_producto(producto_id):
    """
    Elimina permanentemente un producto de la base de datos.
    
    Args:
        producto_id: ID del producto a eliminar
        
    Returns:
        bool: True si la eliminación fue exitosa
        
    Raises:
        ObjectDoesNotExist: Si no se encuentra el producto
        Exception: Para otros errores inesperados
    """
    try:
        with transaction.atomic():
            # Obtener el producto
            producto = Producto.objects.get(pk=producto_id)

            # Eliminar el producto
            producto.delete()

            return True
        
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(f"No se encontró el producto con ID {producto_id}")
    except models.ProtectedError as pe:
        raise Exception(f"No se puede eliminar el productos porque tien relaciones protegidas: {str(pe)}")
    except Exception as e:
        raise Exception(f"Error inesperado al eliminar producto: {str(e)}")
