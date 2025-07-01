from django.db import DatabaseError
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
        categoria_id = request.GET.get('categoria', None)

        productos = obtener_productos()
        if categoria_id and categoria_id != 'all':
            productos = productos.filter(categoria_id=categoria_id)
        context = {
            'productos': productos,
            'categorias': obtener_categorias(),
            'categoria_seleccionada': categoria_id
        }
        return render(request, 'comercio/views/products.html', context)
    except DatabaseError:
        return render(request, 'error.html', {'message': 'Error al cargar productos'})
    


