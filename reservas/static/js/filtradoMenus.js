document.addEventListener('DOMContentLoaded', function () {
    const botones = document.querySelectorAll('#filtros-categorias button');
    const cacheMenus = {};  // Caché en memoria
    const contenedor = document.getElementById('contenedor-menus');
    let cargandoMenus = false;

    botones.forEach(btn => {
        btn.addEventListener('click', function () {
            const categoriaId = this.getAttribute('data-categoria');
            const key = categoriaId || 'todos';

            // Actualizar botones activos
            botones.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Si ya está en caché, usarlo directamente
            if (cacheMenus[key]) {
                contenedor.innerHTML = cacheMenus[key];
                aplicarAnimaciones();
                return;
            }

            // Evitar múltiples llamadas simultáneas
            if (cargandoMenus) return;
            cargandoMenus = true;

            let url = '/api/menus-filtrados/';
            if (categoriaId) url += '?categoria=' + categoriaId;

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.menus.length === 0) {
                        contenedor.innerHTML = '<p class="text-muted">No hay menús en esta categoría.</p>';
                        cacheMenus[key] = contenedor.innerHTML;
                        cargandoMenus = false;
                        return;
                    }

                    let html = '';
                    data.menus.forEach(menu => {
                        html += `
                            <div class="col-6 col-sm-4 col-md-3 mb-4 fade-in">
                                <div class="text-center h-100 px-2">
                                    <img src="${menu.img_url}" class="img-fluid rounded-3 menu-img" alt="${menu.nombre}" loading="lazy">
                                    <p class="fw-bold mt-2 text-uppercase">${menu.nombre}</p>
                                    <p class="text-muted small">${menu.descripcion || ""}</p>
                                </div>
                            </div>
                        `;
                    });

                    contenedor.innerHTML = html;
                    cacheMenus[key] = html;  // Guardar en caché
                    aplicarAnimaciones();
                    cargandoMenus = false;
                })
                .catch(error => {
                    console.error('Error al filtrar menús:', error);
                    cargandoMenus = false;
                });
        });
    });
});

// 🌀 Fade-in suave para elementos
function aplicarAnimaciones() {
    const elementos = document.querySelectorAll('.fade-in');
    elementos.forEach(el => {
        el.style.opacity = 0;
        el.style.transition = 'opacity 0.4s ease-in';
        setTimeout(() => el.style.opacity = 1, 10);
    });
}
