document.addEventListener('DOMContentLoaded', function () {
    // Evento para cada botón de categoría
    const botones = document.querySelectorAll('#filtros-categorias button');

    botones.forEach(btn => {
        btn.addEventListener('click', function () {
            const categoriaId = this.getAttribute('data-categoria');
            filtrarMenus(categoriaId ? parseInt(categoriaId) : null);

            // Actualizar botones activos
            botones.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

let cargandoMenus = false;

function filtrarMenus(categoriaId) {
    if (cargandoMenus) return;  // Evita múltiples fetch si ya está cargando
    cargandoMenus = true;

    let url = '/api/menus-filtrados/';
    if (categoriaId) {
        url += '?categoria=' + categoriaId;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const contenedor = document.getElementById('contenedor-menus');
            contenedor.innerHTML = ''; // Limpiar anterior

            if (data.menus.length === 0) {
                contenedor.innerHTML = '<p class="text-muted">No hay menús en esta categoría.</p>';
                cargandoMenus = false;
                return;
            }

            data.menus.forEach(menu => {
                const col = document.createElement('div');
                col.className = 'col-6 col-sm-4 col-md-3 mb-4 fade-in';
                col.innerHTML = `
                    <div class="text-center h-100 px-2">
                        <img src="${menu.img_url}" class="img-fluid rounded-3 menu-img" alt="${menu.nombre}">
                        <p class="fw-bold mt-2 text-uppercase">${menu.nombre}</p>
                        <p class="text-muted small">${menu.descripcion || ""}</p>
                    </div>
                `;
                contenedor.appendChild(col);
            });

            cargandoMenus = false;
        })
        .catch(error => {
            console.error('Error al filtrar menús:', error);
            cargandoMenus = false;
        });
}
