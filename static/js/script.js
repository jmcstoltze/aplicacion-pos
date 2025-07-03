// Función para mostrar/ocultar el menú
function toggleMenu() {
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    sidebar.classList.toggle('active');
    
    // Solo para móviles (≤768px)
    if (window.innerWidth <= 768) {
        content.classList.toggle('sidebar-active');
    } else {
        // Para pantallas grandes (>768px)
        content.classList.toggle('shifted');
    }
}

// Cerrar menú al hacer clic fuera de él (versión corregida)
document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    const hamburger = document.querySelector('.navbar-toggler-icon');
    const content = document.getElementById('content');
    
    if (!sidebar.contains(event.target) && event.target !== hamburger && !hamburger.contains(event.target)) {
        sidebar.classList.remove('active');
        
        // Elimina ambas clases para asegurar el estado correcto
        content.classList.remove('shifted', 'sidebar-active');
    }
});

// Función para manejar los submenús
document.querySelectorAll('.submenu-toggle').forEach(item => {
    item.addEventListener('click', function(e) {
    e.preventDefault();
    const parent = this.parentElement;
    parent.classList.toggle('active');
            
    // Cerrar otros submenús abiertos
    document.querySelectorAll('.has-submenu').forEach(submenu => {
        if (submenu !== parent && submenu.classList.contains('active')) {
            submenu.classList.remove('active');
        }
    });
});
});

// Función para filtros de categorías
document.getElementById('branchSelect').addEventListener('change', function() {
    
    // Filtrar con AJAX
    fetch(`?categoria=${this.value}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('productos-container').innerHTML = html;
        });
});

// Función para búsqueda en edición de productos
document.getElementById('searchInput').addEventListener('input', function(e) {
    const searchTerm = e.target.value;
    
    // Cancelar peticiones anteriores si existe
    if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
    }
    
    // Esperar 300ms después de que el usuario deja de escribir
    this.searchTimeout = setTimeout(() => {
        fetch(`?search=${encodeURIComponent(searchTerm)}&ajax=1`)
            .then(response => response.text())
            .then(html => {
                document.getElementById('productos-container').innerHTML = html;
            });
    }, 300);
});

// Función para habilitar/deshabilitar el modo edición
function enableEditMode() {
    const editButtons = document.querySelectorAll('.edit-buttons');
    editButtons.forEach(button => {
        button.classList.toggle('d-none');
    });
}

// Función para cargar datos del producto en el modal de edición
function loadProductData(productId) {
    fetch(`/get_product_data/${productId}/`)
        .then(response => response.json())
        .then(data => {
            // Llenar el formulario con los datos del producto
            document.getElementById('editProductId').value = data.id;
            document.getElementById('editProductSKU').value = data.sku;
            document.getElementById('editProductCode').value = data.codigo_barra;
            document.getElementById('editProductCategory').value = data.categoria_id;
            document.getElementById('editProductName').value = data.nombre_producto;
            document.getElementById('editProductAbrName').value = data.nombre_abreviado;
            document.getElementById('editProductDescp').value = data.descripcion;
            document.getElementById('editProductPrice').value = data.precio_venta;
            
            // Mostrar el modal
            const editModal = new bootstrap.Modal(document.getElementById('editProductModal'));
            editModal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al cargar los datos del producto');
        });
}

// Manejar envío del formulario de edición
document.getElementById('editProductForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch('/edicion_productos/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data && data.success) {
            window.location.reload();
        } else if (data) {
            alert(data.message || 'Error al actualizar el producto');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al actualizar el producto');
    });
});

// Cambio automático del año en el footer
document.getElementById('year').textContent = new Date().getFullYear();

document.addEventListener('DOMContentLoaded', function () {
    const logoutLink = document.getElementById('logoutLink');

    logoutLink.addEventListener('click', function (e) {
        e.preventDefault(); // Evita la navegación inmediata

        const confirmLogout = confirm("¿Está seguro de que desea cerrar sesión?");
        if (confirmLogout) {
            // Redirecciona manualmente al logout
            window.location.href = logoutLink.getAttribute('data-logout-url');
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const logoutLink = document.getElementById('logoutLink2');

    logoutLink.addEventListener('click', function (e) {
        e.preventDefault(); // Evita la navegación inmediata

        const confirmLogout = confirm("¿Está seguro de que desea cerrar sesión?");
        if (confirmLogout) {
            // Redirecciona manualmente al logout
            window.location.href = logoutLink.getAttribute('data-logout-url');
        }
    });
});
