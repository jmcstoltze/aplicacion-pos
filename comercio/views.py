from django.db import models
from django.db import DatabaseError
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from decimal import Decimal, InvalidOperation
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Producto
from .services import (
    obtener_productos,
    obtener_categorias,
    crear_producto,    
    editar_producto,
    deshabilitar_producto,
    listar_productos,
    eliminar_producto
)

@login_required
def edicion_productos(request) -> HttpResponse | HttpResponseRedirect:
    try:

        categoria = request.GET.get('categoria', None)
        search_query = request.GET.get('search', None)
        productos = obtener_productos()

        # Manejo del formulario para deshabilitar o "eliminar" productos
        if request.method == 'POST' and 'deshabilitar_producto' in request.POST:
            try:
                producto_id = request.POST.get('producto_id')
                success, message = deshabilitar_producto(producto_id)

                if success:
                    messages.success(request, message)
                else:
                    messages.warning(request, message)

                return redirect('edicion_productos')
            
            except ObjectDoesNotExist as e:
                messages.error(request, str(e))
                return redirect('edicion_productos')
            except Exception as e:
                messages.error(request, f'Error al deshabilitar producto: {str(e)}')
                return redirect('edicion_productos')


        # Manejo del formulario de agregar producto
        if request.method == 'POST' and 'agregar_producto' in request.POST:

            try:
                # Convertir precio_venta a Decimal
                precio_str = request.POST.get('productPrice')
                precio_venta = None
                if precio_str:
                    try:
                        precio_venta = Decimal(precio_str)
                    except InvalidOperation:
                        raise ValidationError("El precio debe ser un número válido")

                # Crear el producto
                crear_producto(
                    sku=request.POST.get('productSKU').strip(),
                    codigo_barra=request.POST.get('productCode').strip(),
                    nombre_producto=request.POST.get('productName').strip(),
                    nombre_abreviado=request.POST.get('productAbrName').strip(),
                    descripcion=request.POST.get('productDescp').strip(),
                    categoria_id=request.POST.get('productCategory'),
                    precio_venta=precio_venta,
                    imagen=request.FILES.get('productImage'),
                    disponible=True
                )
                messages.success(request, 'Producto agregado exitosamente')

                return redirect('edicion_productos') # Redirige a la misma vista
                # Recargar los productos después de agregar uno nuevo
                # productos = obtener_productos()
            
            except ValidationError as e:
                messages.error(request, f'Error de validación: {str(e)}')
                return redirect('edicion_productos')
            except Exception as e:
                messages.error(request, f'Error al guardar producto: {str(e)}')
                return redirect('edicion_productos')

        # Manejor del formulario de edición de producto
        if request.method == 'POST' and 'editar_producto' in request.POST:
            try:
                producto_id = request.POST.get('product_id')
                precio_str = request.POST.get('editProductPrice')
                precio_venta = None
                if precio_str:
                    try:
                        precio_venta = Decimal(precio_str)
                    except InvalidOperation:
                        raise ValidationError("El precio debe ser un número válido")
                    
                # Prepara datos para edición
                update_data = {
                    'nombre_producto': request.POST.get('editProductName').strip(),
                    'nombre_abreviado': request.POST.get('editProductAbrName').strip(),
                    'descripcion': request.POST.get('editProductDescp').strip(),
                    'precio_venta': precio_venta,
                    'categoria_id': request.POST.get('editProductCategory')
                }

                # Editar el producto
                editar_producto(
                    producto_id=producto_id,
                    imagen=request.FILES.get('editProductImage'),
                    **update_data
                )

                messages.success(request, 'Producto actualizado exitosamente')
                return redirect('edicion_productos')
                # productos = obtener_productos()
            
            except ValidationError as e:
                messages.error(request, f'Error de validación: {str(e)}')
                return redirect('edicion_productos')
            except Exception as e:
                messages.error(request, f'Error al actualizar producto: {str(e)}')
                return redirect('edicion_productos')

        # Filtrar por categoría si se especifica
        if categoria and categoria != 'all':
            productos = productos.filter(categoria=categoria)
        
        # Filtrar por término de búsqueda si se especifica (búsqueda parcial)
        if search_query:
            # Búsqueda insensible a acentos 
            productos = productos.filter(
                models.Q(nombre_producto__icontains=search_query) |
                models.Q(sku__icontains=search_query) |
                models.Q(codigo_barra__icontains=search_query)
            )
        
        context = {
            'productos': productos,
            'categorias': obtener_categorias(),
            'categoria_seleccionada': categoria,
            'search_query': search_query
        }
        return render(request, 'comercio/views/products.html', context)
    except DatabaseError as e:
        return render(request, 'error.html', {'message': 'Error al cargar productos'})
    


