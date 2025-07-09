document.addEventListener("DOMContentLoaded", function () {
    // --------------------------
    // Botones login/register
    // --------------------------
    const container = document.getElementById('container');
    const registerBtn = document.getElementById('register');
    const loginBtn = document.getElementById('login');

    if (registerBtn && loginBtn && container) {
        registerBtn.addEventListener('click', () => container.classList.add("active"));
        loginBtn.addEventListener('click', () => container.classList.remove("active"));
    }

    // --------------------------
    // Enlace WhatsApp dinámico
    // --------------------------
    const enlaceWhatsapp = document.getElementById('btn-whatsapp');
    if (enlaceWhatsapp) {
        const numero = "595971327887";
        const mensaje = "Hola FoodFusion, tengo una consulta.";
        enlaceWhatsapp.href = `https://wa.me/${numero}?text=${encodeURIComponent(mensaje)}`;
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
                    finInput.value = nuevaHora.toTimeString().slice(0, 5);
                    finPicker.setDate(finInput.value, true);
                }
            }
        });
    }

    // --------------------------
    // Reserva con AJAX + SweetAlert PROCESANDO
    // --------------------------
    const reservarForms = document.querySelectorAll("form[action*='reservar/']");

    reservarForms.forEach(form => {
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            Swal.fire({
                title: 'Procesando reserva...',
                html: 'Por favor, espera unos segundos.',
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });

            const formData = new FormData(form);

            fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": formData.get("csrfmiddlewaretoken")
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Reserva confirmada!',
                        text: 'Tu reserva ha sido realizada con éxito.',
                        showConfirmButton: false,
                        timer: 1000
                    }).then(() => {
                        location.href = "/mis-reservas/";
                    });
                } else {
                    Swal.fire("Error", data.error || "Ocurrió un error al reservar.", "error");
                }
            })
            .catch(err => {
                Swal.fire("Error", "No se pudo conectar con el servidor.", "error");
                console.error(err);
            });
        });
    });

    // --------------------------
    // Cancelación con AJAX + SweetAlert
    // --------------------------
    const cancelarForms = document.querySelectorAll("form[action*='cancelar/']");

    cancelarForms.forEach(form => {
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            Swal.fire({
                title: '¿Cancelar reserva?',
                text: 'Esta acción no se puede deshacer.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sí, cancelar',
                cancelButtonText: 'No'
            }).then((result) => {
                if (!result.isConfirmed) return;

                Swal.fire({
                    title: 'Procesando cancelación...',
                    html: 'Por favor, espera...',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });

                const formData = new FormData(form);

                fetch(form.action, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": formData.get("csrfmiddlewaretoken")
                    }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Reserva cancelada',
                            text: 'Tu reserva fue cancelada correctamente.',
                            showConfirmButton: false,
                            timer: 1000
                        }).then(() => {
                            location.reload();
                        });
                    } else {
                        Swal.fire("Error", data.error || "Ocurrió un error al cancelar.", "error");
                    }
                })
                .catch(err => {
                    Swal.fire("Error", "No se pudo conectar con el servidor.", "error");
                    console.error(err);
                });
            });
        });
    });
});
