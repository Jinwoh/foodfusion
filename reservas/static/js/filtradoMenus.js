function filtrarMenus(categoriaId) {
    let url = '/api/menus-filtrados/';
    if (categoriaId) {
        url += '?categoria=' + categoriaId;
    }

    // Actualizar botones activos
    document.querySelectorAll('#filtros-categorias button').forEach(btn => {
        btn.classList.remove('active');
    });
    if (categoriaId === null) {
        document.querySelector('#filtros-categorias button').classList.add('active');
    } else {
        const buttons = document.querySelectorAll('#filtros-categorias button');
        buttons.forEach(btn => {
            if (btn.getAttribute('onclick') === `filtrarMenus(${categoriaId})`) {
                btn.classList.add('active');
            }
        });
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const contenedor = document.getElementById('contenedor-menus');
            contenedor.innerHTML = ''; // Limpiar anterior

            if (data.menus.length === 0) {
                contenedor.innerHTML = '<p class="text-muted">No hay menús en esta categoría.</p>';
                return;
            }

            data.menus.forEach(menu => {
                const col = document.createElement('div');
                col.className = 'col-6 col-sm-4 col-md-3 mb-4';
                col.innerHTML = `
                    <div class="text-center">
                        <img src="${menu.img_url}" class="img-fluid" style="width: 100%; height: 180px; object-fit: cover; border-radius: 10px;">
                        <p class="fw-bold mt-2 text-uppercase">${menu.nombre}</p>
                    </div>
                `;
                contenedor.appendChild(col);
            });
        })
        .catch(error => console.error('Error al filtrar menús:', error));
}

