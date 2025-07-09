document.addEventListener("DOMContentLoaded", function () {
    // --------------------------
    // Botones login/register
    // --------------------------
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

    // --------------------------
    // Enlace WhatsApp dinámico
    // --------------------------
    const enlaceWhatsapp = document.getElementById('btn-whatsapp');
    if (enlaceWhatsapp) {
        const numero = "595971327887";
        const mensaje = "Hola FoodFusion, tengo una consulta.";
        const url = `https://wa.me/${numero}?text=${encodeURIComponent(mensaje)}`;
        enlaceWhatsapp.href = url;
    }

    // --------------------------
    // Flatpickr para horarios
    // --------------------------
    const inicioInput = document.getElementById("hora_inicio");
const finInput = document.getElementById("hora_fin");

if (inicioInput && finInput) {
    const horaInicioValor = inicioInput.value || "17:00";
    const horaFinValor = finInput.value || "17:30";

    const finPicker = flatpickr(finInput, {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
        time_24hr: true,
        minTime: "17:00",
        maxTime: "22:00",
        minuteIncrement: 30,
        defaultDate: horaFinValor
    });

    flatpickr(inicioInput, {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
        time_24hr: true,
        minTime: "17:00",
        maxTime: "22:00",
        minuteIncrement: 30,
        defaultDate: horaInicioValor,
        onChange: function (selectedDates) {
            if (selectedDates.length > 0) {
                let nuevaHora = new Date(selectedDates[0].getTime() + 60 * 60 * 1000);
                let horas = nuevaHora.getHours().toString().padStart(2, '0');
                let minutos = nuevaHora.getMinutes().toString().padStart(2, '0');
                let nuevaHoraStr = `${horas}:${minutos}`;
                finInput.value = nuevaHoraStr;
                finPicker.setDate(nuevaHoraStr, true);
            }
        }
    });
}


    // --------------------------
    // Procesar formularios de reserva con AJAX
    // --------------------------
    const modalElement = document.getElementById("modalProcesando");
    const gifCargando = document.getElementById("gif-cargando");
    const gifVerificado = document.getElementById("gif-verificado");
    const modalTexto = document.getElementById("modalTexto");

    const forms = document.querySelectorAll("form[action*='reservar/']");

    if (modalElement && forms.length > 0) {
        const modal = new bootstrap.Modal(modalElement);

        forms.forEach(form => {
            form.addEventListener("submit", function (e) {
                e.preventDefault();

                modalTexto.textContent = "Procesando reserva...";
                gifCargando.classList.remove("d-none");
                gifVerificado.classList.add("d-none");
                modal.show();

                const formData = new FormData(form);

                fetch(form.action, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": formData.get('csrfmiddlewaretoken')
                    }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        gifCargando.classList.add("d-none");
                        gifVerificado.classList.remove("d-none");
                        modalTexto.textContent = "✅ ¡Reserva realizada con éxito!";
                        setTimeout(() => {
                            location.href = "/mis-reservas/";
                        }, 1500);
                    } else {
                        modal.hide();
                        alert("❌ " + (data.error || "Ocurrió un error al reservar."));
                    }
                })
                .catch(err => {
                    modal.hide();
                    alert("❌ Error al conectar con el servidor.");
                    console.error(err);
                });
            });
        });
    }
});
