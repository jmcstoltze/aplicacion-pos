from django.db import models
from django.db import DatabaseError
from django.core.exceptions import ValidationError
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
    listar_productos,
    editar_producto,
    eliminar_producto
)

@login_required
def edicion_productos(request) -> HttpResponse | HttpResponseRedirect:
    try:
        # Manejo del formulario de agregar producto
        if request.method == 'POST' and 'agregar_producto' in request.POST:

            try:
                # Crear rl producto usando tu función existente
                producto = crear_producto(
                    sku=request.POST.get('sku'),
                    codigo_barra=request.POST.get('codigo_barra'),
                    nombre_producto=request.POST.get('nombre_producto'),
                    nombre_abreviado=request.POST.get('nombre_abreviado'),
                    descripcion=request.POST.get('descripcion'),
                    categoria_id=request.POST.get('categoria'),
                    precio_venta=request.POST.get('precio_venta'),
                    imagen=request.FILES.get('imagen')
                )
                messages.success(request, 'Producto agregado exitosamente')

                return redirect('edicion_productos')
            
            except ValidationError as e:
                messages.error(request, f'Error de validación: {str(e)}')
            except Exception as e:
                messages.error(request, f'Error al guardar producto: {str(e)}')
                



        categoria_id = request.GET.get('categoria', None)
        search_query = request.GET.get('search', None)

        productos = obtener_productos()

        # Filtrar por categoría si se especifica
        if categoria_id and categoria_id != 'all':
            productos = productos.filter(categoria_id=categoria_id)
        
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
            'categoria_seleccionada': categoria_id,
            'search_query': search_query
        }
        return render(request, 'comercio/views/products.html', context)
    except DatabaseError:
        return render(request, 'error.html', {'message': 'Error al cargar productos'})
    


