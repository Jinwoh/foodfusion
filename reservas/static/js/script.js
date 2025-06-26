document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('container');
    const registerBtn = document.getElementById('register');
    const loginBtn = document.getElementById('login');

    if (registerBtn && loginBtn && container) {
        registerBtn.addEventListener('click', () => {
            container.classList.add("active");
        });

        loginBtn.addEventListener('click', () => {
            container.classList.remove("active");
        });
    }

    const enlaceWhatsapp = document.getElementById('btn-whatsapp');

    if (enlaceWhatsapp) {
        const numero = "595971327887";
        const mensaje = "Hola FoodFusion, tengo una consulta.";
        const url = `https://wa.me/${numero}?text=${encodeURIComponent(mensaje)}`;
        enlaceWhatsapp.href = url;
        console.log("✅ Enlace actualizado:", url);
    } else {
        console.warn("❌ No se encontró el botón de WhatsApp");
    }
});
