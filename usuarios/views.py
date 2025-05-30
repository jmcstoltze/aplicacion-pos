from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from services import obtener_user, obtener_usuario

def inicio_sesion(request):
    """
    Maneja el proceso de autenticación y redirección de usuarios según su rol.
    
    Esta vista procesa el formulario de inicio de sesión, autentica al usuario
    y lo redirige a la interfaz correspondiente según su rol en el sistema:
    - Superusuario: Panel de administración de Django (/admin/)
    - Administradores: Dashboard de administrador
    - Jefes de Local: Dashboard de jefe de local
    - Cajeros: Dashboard de cajero

    Args:
        request (HttpRequest): Objeto de solicitud HTTP que contiene los datos del formulario.

    Returns:
        HttpResponseRedirect: Redirección al dashboard correspondiente si la autenticación es exitosa.
        HttpResponse: Renderizado de la plantilla de inicio de sesión con mensajes de error si falla.

    Raises:
        PermissionDenied: Si el usuario autenticado no tiene un rol válido asignado.

    Example:
        >>> # Acceso vía POST con credenciales válidas
        >>> response = client.post('/login/', {'username': 'admin', 'password': 'secret'})
        >>> response.status_code
        302  # Redirección
    """

    if request.method == 'POST':
        # Obtiene los datos POST del formulario
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = obtener_user(username) # Obtiene el usuario Auth_User

        # Si el usuario no existe lo indica
        if not user:
            return render(request, 'inicio_sesion.html', {'error_message': 'Usuario no existe'})
        
        # Autentica al usuario y contraseña
        usuario_autenticado = authenticate(request, username=user.username, password=password)

        # Si usuario existe lo logea
        if usuario_autenticado:
            login(request, usuario_autenticado)

            # Verifica si usuario logeado es superusuario
            if usuario_autenticado.is_superuser:
                # Redirige a panel de administración de Django
                return redirect('/admin/')

            usuario = obtener_usuario(user) # Obtiene el Usuario

            # Redirección según rol de usuario
            if usuario.rol.nombre_rol == 'Administrador':
                return redirect('dashboard_administrador')
            elif usuario.rol.nombre_rol == 'Jefe de Local':
                return redirect('dashboard_jefe_local')
            elif usuario.rol.nombre_rol == 'Cajero':
                return redirect('dashboard_cajero')
            else:
                # Manejo de roles no reconocidos
                logout(request)
                return render(request, 'inicio_sesion.html', {'error_message': 'Rol de usuario no válido'})
        else:
            # Credenciales inválidas
            return render(request, 'inicio_sesion.html', {'error_message': 'Contraseña incorrecta'})
    else:
        # Método GET muestra el formulario
        return render(request, "inicio_sesion.html", {}) # Renderiza la página




        
        


            