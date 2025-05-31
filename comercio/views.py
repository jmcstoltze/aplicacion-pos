from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Producto
from .services import (
    crear_producto,
    listar_productos,
    editar_producto,
    eliminar_producto
)
