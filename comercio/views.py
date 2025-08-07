from django.db import models
from django.db import DatabaseError, IntegrityError
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from decimal import Decimal, InvalidOperation
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Producto, StockBodega, Bodega
from .services import (
    obtener_productos,
    obtener_categorias,
    crear_producto,    
    editar_producto,
    deshabilitar_producto,
    listar_productos,
    eliminar_producto,
    obtener_bodegas,
    obtener_productos_con_stock,
    productos_bodega,
    exportar_stock_csv,
    obtener_sucursales
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

@login_required
def stock_productos(request) -> HttpResponse | HttpResponseRedirect:

    # Contexto inicial como diccionario normal
    initial_context = {
        'productos': Producto.objects.none(),
        'bodegas': Bodega.objects.all(),
        'bodega_seleccionada': 'all',
        'productos_con_stock': 0,
        'total_productos': 0
    }
    
    try:
        # Obtiene ID de bodega de los parámetros GET u 'all' por defecto
        bodega_id = request.GET.get('bodega', 'all')

        # Consulta todos los productos
        productos = Producto.objects.all()

        # Prefetch optimizado para relaciones de stock
        prefetch_query = StockBodega.objects.select_related('bodega')
        
        # Si se filtra por bodega específica, aplica el filtro
        if bodega_id != 'all':
            prefetch_query = prefetch_query.filter(bodega_id=bodega_id)
        
        # Aplica el prefetch a la consulta principal
        productos = productos.prefetch_related(
            models.Prefetch('stockbodega_set', queryset=prefetch_query, to_attr='stocks_filtrados')
        )

        # Calcula stock total si se seleccionan todas la bodegas
        if bodega_id == 'all':
            productos = productos.annotate(
            stock_total=models.Sum('stockbodega__stock')
            )

            # Contar productos con stock total > 0
            productos_con_stock = productos.filter(stock_total__gt=0).count()

        # Calcula stock por bodega si se filtró
        else:
            productos = productos.annotate(
            stock_bodega=models.Sum(
                'stockbodega__stock',
                filter=models.Q(stockbodega__bodega_id=bodega_id)
                )
            )

            # Contar productos con stock en esta bodega > 0
            productos_con_stock = productos.filter(stock_bodega__gt=0).count()

        # Crear nuevo diccionario de contexto combinando el inicial con los nuevos valores
        context = {
            **initial_context,
            'productos': productos.order_by('categoria__nombre_categoria', 'nombre_producto'),
            'bodega_seleccionada': bodega_id,
            'productos_con_stock': productos_con_stock,
            'total_productos': productos.count()
        }
        
        # Manejar habilitación de producto
        if 'habilitar_producto' in request.GET:
            try:
                producto = Producto.objects.get(id=request.GET['habilitar_producto'])
                producto.disponible = True
                producto.save()
                messages.success(request, f'"{producto.nombre_producto}" disponible en todas la bodegas')
                return redirect('stock_productos') # Redirige sin parámetros para refrescar
            
            except Producto.DoesNotExist:
                messages.error(request, 'Error: Producto no encontrado')
                return redirect('stock_productos')

        # Manejar POST (ajustes de stock)
        if request.method == 'POST':
            if bodega_id == 'all':
                messages.error(request, 'Debes seleccionar una bodega específica para hacer ajustes')
                # Mantener el render en lugar de redirect
                return render(request, 'comercio/views/stock.html', context)
        
            # Procesar ajustes individuales/masivos
            for key, value in request.POST.items():
                if key.startswith('ajuste_'):
                    producto_id = key.replace('ajuste_', '')
                    p = Producto.objects.get(id=producto_id)

                    try:
                        ajuste = int(value)
                        if ajuste == 0:
                            continue

                        # Actualizar stock
                        stock, created = StockBodega.objects.get_or_create(
                            producto_id=producto_id,
                            bodega_id=bodega_id,
                            defaults={'stock': 0}
                        )
                        stock.stock += ajuste
                        if stock.stock < 0:
                            messages.error(request, f'"{p.nombre_producto}" no puede tener stock negativo')
                        else:
                            stock.save()
                            messages.success(request, f'Stock actualizado para "{p.nombre_producto}"')
                
                    except (ValueError, IntegrityError) as e:
                        messages.error(request, f'Error al actualizar "{p.nombre_producto}": {str(e)}')
                
            return redirect(f"{reverse('stock_productos')}?bodega={bodega_id}")                        

        # Mantener el render en lugar de redirect
        return render(request, 'comercio/views/stock.html', context)
    
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return render(request, 'comercio/views/stock.html', context)
    
@login_required
def asignacion_sucursales(request) -> HttpResponse | HttpResponseRedirect:

    sucursales = obtener_sucursales()

    return render(request, 'comercio/views/sucursales.html', context = {'sucursales': sucursales})

@login_required
def asignacion_cajas(request) -> HttpResponse | HttpResponseRedirect:
    return render(request, 'comercio/views/cajas.html', context = {})

