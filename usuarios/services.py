from django.contrib.auth.models import User
from usuarios.models import Usuario

def obtener_user(username: str) -> User | None:
    """
    Obtiene un usuario del sistema de autenticación mediante su username.

    Esta función busca en la tabla de usuarios de Django (auth_user) por el username
    exacto y retorna el objeto User correspondiente, si existe.

    Args:
        username (str): Nombre de usuario a buscar (case-sensitive).

    Returns:
        User | None: Instancia del modelo User si se encuentra, None si no existe.

    Raises:
        User.DoesNotExist, ValueError, TypeError: múltiples excepciones potenciales.

    Example:
        >>> user = obtener_user('usuario1')
        >>> if user:
        ...     print(f"Usuario encontrado: {user.email}")
    """
    try:
        return User.objects.get(username=username)
    except (User.DoesNotExist, ValueError, TypeError):
        return None
    
def obtener_usuario(user: User) -> Usuario | None:
    """
    Obtiene el usuario extendido (Usuario) asociado a un User de Django.

    Busca en el modelo extendido Usuario (relacionado con OneToOne a User) y retorna
    la instancia correspondiente al User proporcionado.

    Args:
        user (User): Instancia del modelo User de Django al que está asociado el Usuario.

    Returns:
        Usuario | None: Instancia del modelo Usuario si existe, None si no se encuentra.

    Raises:
        Usuario.DoesNotExist, ValueError, TypeError): múltiples excepciones potenciales.

    Example:
        >>> from django.contrib.auth.models import User
        >>> user = User.objects.get(pk=1)
        >>> usuario = obtener_usuario(user)
        >>> if usuario:
        ...     print(f"Perfil extendido: {usuario.telefono}")
    """
    try:
        return Usuario.objects.get(user=user)
    except (Usuario.DoesNotExist, ValueError, TypeError):
        return None
