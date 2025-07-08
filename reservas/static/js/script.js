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
        console.log("✅ Enlace actualizado:", url);
    } else {
        console.warn("❌ No se encontró el botón de WhatsApp");
    }

    // --------------------------
    // Flatpickr para horarios de reserva
    // --------------------------
    const inicioInput = document.getElementById("hora_inicio");
    const finInput = document.getElementById("hora_fin");

    if (inicioInput && finInput) {
        const finPicker = flatpickr(finInput, {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            time_24hr: true,
            minTime: "17:00",
            maxTime: "22:00",
            minuteIncrement: 30,
            defaultDate: "17:30" // <- valor por defecto más lógico para fin
        });

        flatpickr(inicioInput, {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            time_24hr: true,
            minTime: "17:00",
            maxTime: "22:00",
            minuteIncrement: 30,
            defaultDate: "17:00", // <- valor por defecto para inicio
            onChange: function (selectedDates, dateStr) {
                if (selectedDates.length > 0) {
                    let nuevaHora = new Date(selectedDates[0].getTime() + 60 * 60 * 1000); // +1 hora
                    let horas = nuevaHora.getHours().toString().padStart(2, '0');
                    let minutos = nuevaHora.getMinutes().toString().padStart(2, '0');
                    let nuevaHoraStr = `${horas}:${minutos}`;
                    finInput.value = nuevaHoraStr;
                    finPicker.setDate(nuevaHoraStr, true);
                }
            }
        });
    }
});
