document.addEventListener('DOMContentLoaded', function() {
    // Función auxiliar para obtener el valor de una cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const trimmed = cookie.trim();
                if (trimmed.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    // Obtener todas las actividades
    const actividades = document.querySelectorAll('.actividad');
    // Índice de la actividad actual
    let actividadActual = 0;
    // Total de actividades
    const totalActividades = actividades.length;
    // Barra de progreso
    const progressBar = document.querySelector('.progress-bar');

    // Función para mostrar actividad actual y ocultar las demás
    function mostrarActividad(index) {
        // Validar índice
        if (index < 0 || index >= totalActividades) {
            console.error('Índice de actividad inválido:', index);
            return;
        }

        // Ocultar todas las actividades
        actividades.forEach((actividad, i) => {
            if (i === index) {
                actividad.style.display = 'block';
            } else {
                actividad.style.display = 'none';
            }
        });

        // Actualizar barra de progreso
        const porcentaje = ((index + 1) / totalActividades) * 100;
        progressBar.style.width = porcentaje + '%';
        progressBar.setAttribute('aria-valuenow', porcentaje);

        // Actualizar botones según sea necesario
        updateNavigationButtons(index);

        // Actualizar URL para mantener el estado (opcional)
        actualizarURL(index);

        console.log('Mostrando actividad', index + 1, 'de', totalActividades);
    }

    // Función para actualizar los botones de navegación
    function updateNavigationButtons(index) {
        // Actualizar texto del botón según sea la última actividad o no
        const botonActual = actividades[index].querySelector('.btn-blue, .validar-imagenes');
        if (botonActual) {
            if (index === totalActividades - 1) {
                botonActual.textContent = 'Ver Resultados';
                botonActual.setAttribute('name', 'finish');
            } else {
                botonActual.textContent = 'Siguiente';
                botonActual.setAttribute('name', 'next');
            }
        }
    }

    // Función para navegar a la siguiente actividad
    function siguienteActividad() {
        // Solo avanzar si hay más actividades
        if (actividadActual < totalActividades - 1) {
            actividadActual++;
            mostrarActividad(actividadActual);
        } else {
            // En caso de ser la última actividad, redirigir a la página de resultados
            window.location.href = '/result_form/';
        }
    }

    // Función para validar la actividad actual y guardar la respuesta
    function validarActividad(actividadElement) {
        const preguntaId = actividadElement.dataset.preguntaId;
        const topicId = actividadElement.dataset.topicId;
        const subtopicId = actividadElement.dataset.subtopicId;

        // Implementar lógica específica de validación según la actividad
        // Por ejemplo, para la actividad de selección de imágenes
        if (preguntaId === "1") {
            const seleccionadas = actividadElement.querySelectorAll('.image-item.selected');
            const seleccionadasIds = Array.from(seleccionadas).map(item => parseInt(item.dataset.id));
            const respuestasCorrectas = actividadElement.dataset.respuesta.split(',').map(r => parseInt(r));

            const esCorrecta = respuestasCorrectas.every(id => seleccionadasIds.includes(id)) &&
                              seleccionadasIds.every(id => respuestasCorrectas.includes(id));

            // Enviar la respuesta al backend
            fetch('/guardar_respuesta/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    activity_id: preguntaId,
                    activity_type: 'seleccion_imagenes',
                    user_response: seleccionadasIds,
                    is_correct: esCorrecta,
                    subtopic_id: subtopicId
                })
            }).catch(error => console.error('Error al guardar respuesta:', error));
        }

        // Para otros tipos de actividades, el código existente de event listeners
        // ya debería estar manejando la validación y envío.

        return true; // Permitir continuar (en un caso real, deberías validar primero)
    }

    // Inicializar: ocultar todas las actividades primero
    actividades.forEach(actividad => {
        actividad.style.display = 'none';
    });

    // Mostrar solo la primera actividad
    mostrarActividad(0);

    // Agregar event listeners a los botones de "Siguiente" y "Ver Resultados"
    document.querySelectorAll('.btn-blue, .validar-imagenes').forEach(boton => {
        boton.addEventListener('click', function(event) {
            event.preventDefault();

            // Validar la actividad actual antes de avanzar
            const actividadElement = actividades[actividadActual];
            const esValida = validarActividad(actividadElement);

            if (esValida) {
                // Si es la última actividad y el botón dice "Ver Resultados"
                if (actividadActual === totalActividades - 1 && (this.name === 'finish' || this.textContent.trim() === 'Ver Resultados')) {
                    // Redirigir a la página de resultados
                    window.location.href = '/result_form/';
                } else {
                    // Avanzar a la siguiente actividad
                    siguienteActividad();
                }
            }
        });
    });

    // Verificar si hay un parámetro 'activity' en la URL
    function cargarActividadDesdeURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const activityParam = urlParams.get('activity');

        if (activityParam && !isNaN(activityParam)) {
            const index = parseInt(activityParam) - 1;
            if (index >= 0 && index < totalActividades) {
                actividadActual = index;
                mostrarActividad(index);
            }
        }
    }

    // Actualizar la URL para mantener el estado
    function actualizarURL(index) {
        const url = new URL(window.location.href);
        url.searchParams.set('activity', index + 1);
        window.history.replaceState({}, '', url);
    }

    // Intentar cargar desde URL al iniciar
    cargarActividadDesdeURL();
});