document.addEventListener('DOMContentLoaded', function () {
    const botones = document.querySelectorAll('#filtros-categorias button');

    botones.forEach(btn => {
        btn.addEventListener('click', function () {
            const categoriaId = this.getAttribute('data-categoria');
            const id = parseInt(categoriaId);
            filtrarMenus(!isNaN(id) ? id : null);

            // Actualizar botones activos
            botones.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

function filtrarMenus(categoriaId) {
    let url = '/api/menus-filtrados/';
    if (categoriaId) {
        url += '?categoria=' + categoriaId;
    }

    const contenedor = document.getElementById('contenedor-menus');
    contenedor.innerHTML = '<p class="text-muted">Cargando menús...</p>'; // Mensaje opcional mientras carga

    fetch(url)
        .then(response => response.json())
        .then(data => {
            contenedor.innerHTML = ''; // Limpiar anterior

            if (!data || !Array.isArray(data.menus)) {
                contenedor.innerHTML = '<p class="text-danger">Error al cargar menús.</p>';
                return;
            }

            if (data.menus.length === 0) {
                contenedor.innerHTML = '<p class="text-muted">No hay menús en esta categoría.</p>';
                return;
            }

            data.menus.forEach(menu => {
                const col = document.createElement('div');
                col.className = 'col-6 col-sm-4 col-md-3 mb-4';
                col.innerHTML = `
                    <img src="${menu.img_url}" class="img-fluid rounded-3">
                    <p class="fw-bold mt-2 text-uppercase">${menu.nombre}</p>
                `;
                contenedor.appendChild(col);
            });
        })
        .catch(error => {
            console.error('Error al filtrar menús:', error);
            contenedor.innerHTML = '<p class="text-danger">No se pudo cargar los menús.</p>';
        });
}
