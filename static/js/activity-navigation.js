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

    // Registrar para depuración
    console.log('activity-navigation.js cargado');

    // Obtener todas las actividades
    const actividades = document.querySelectorAll('.actividad');
    console.log('Actividades encontradas:', actividades.length);

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
        if (progressBar) {
            const porcentaje = ((index + 1) / totalActividades) * 100;
            progressBar.style.width = porcentaje + '%';
            progressBar.setAttribute('aria-valuenow', porcentaje);
        }

        // Actualizar botones según sea necesario
        updateNavigationButtons(index);

        // Actualizar URL para mantener el estado (opcional)
        actualizarURL(index);

        console.log('Mostrando actividad', index + 1, 'de', totalActividades);
    }

    // Función para actualizar los botones de navegación
    function updateNavigationButtons(index) {
        // Actualizar texto del botón según sea la última actividad o no
        if (actividades[index]) {
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
    }

    // Función mejorada para dirigir a resultados
    function dirigirAResultados() {
        console.log('Intentando redirigir a resultados...');

        // Primero intentar redirección directa
        if (verificarSiExisteRuta('/result_form/')) {
            window.location.href = '/result_form/';
        } else if (verificarSiExisteRuta('/results/')) {
            window.location.href = '/results/';
        } else {
            // Si ambas rutas fallan, mostrar un mensaje y usar la primera ruta
            console.warn('No se pudo verificar las rutas, intentando redirección directa');
            window.location.href = '/result_form/';
        }
    }

    // Función para verificar si una ruta existe
    function verificarSiExisteRuta(ruta) {
        try {
            const xhr = new XMLHttpRequest();
            xhr.open('HEAD', ruta, false); // Síncrono para simplificar
            xhr.send();
            return xhr.status !== 404;
        } catch (e) {
            console.error('Error al verificar ruta:', e);
            return true; // Asumir que existe si hay error
        }
    }

    // Función para navegar a la siguiente actividad
    function siguienteActividad() {
        console.log('Función siguienteActividad llamada', actividadActual, totalActividades);

        // Solo avanzar si hay más actividades
        if (actividadActual < totalActividades - 1) {
            actividadActual++;
            mostrarActividad(actividadActual);
        } else {
            console.log('Es la última actividad, redirigiendo a resultados');
            // En caso de ser la última actividad, redirigir a la página de resultados
            dirigirAResultados();
        }
    }

    // Función para validar la actividad actual y guardar la respuesta
    function validarActividad(actividadElement) {
        if (!actividadElement) {
            console.error('Elemento de actividad no encontrado');
            return true; // Permitir continuar para evitar bloqueo
        }

        const preguntaId = actividadElement.dataset.preguntaId;
        const topicId = actividadElement.dataset.topicId;
        const subtopicId = actividadElement.dataset.subtopicId;

        console.log('Validando actividad:', preguntaId);

        // Implementar lógica específica de validación según la actividad
        // Por ejemplo, para la actividad de selección de imágenes
        if (preguntaId === "1") {
            const seleccionadas = actividadElement.querySelectorAll('.image-item.selected');
            const seleccionadasIds = Array.from(seleccionadas).map(item => parseInt(item.dataset.id));

            // Obtener respuestas correctas (con manejo de errores)
            let respuestasCorrectas = [];
            if (actividadElement.dataset.respuesta) {
                try {
                    respuestasCorrectas = actividadElement.dataset.respuesta
                        .split(',')
                        .map(r => parseInt(r.trim()));
                } catch (e) {
                    console.error('Error al parsear respuestas correctas:', e);
                }
            }

            const esCorrecta = respuestasCorrectas.length > 0 ?
                            (respuestasCorrectas.every(id => seleccionadasIds.includes(id)) &&
                            seleccionadasIds.every(id => respuestasCorrectas.includes(id))) : false;

            // Datos para enviar
            const datos = {
                activity_id: preguntaId,
                activity_type: 'seleccion_imagenes',
                user_response: seleccionadasIds,
                is_correct: esCorrecta,
                subtopic_id: subtopicId || '1' // Valor por defecto si no existe
            };

            // Guardar copia local primero
            guardarRespuestaLocal(datos);

            // Enviar la respuesta al backend
            fetch('/guardar_respuesta/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(datos)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                console.log('Respuesta guardada exitosamente:', data);
            })
            .catch(error => {
                console.error('Error al guardar respuesta:', error);
            });
        }

        return true; // Permitir continuar
    }

    // Función para guardar respuesta local
    function guardarRespuestaLocal(datos) {
        try {
            const respuestasGuardadas = JSON.parse(localStorage.getItem('respuestas_backup')) || [];
            respuestasGuardadas.push({
                timestamp: new Date().toISOString(),
                datos: datos
            });
            localStorage.setItem('respuestas_backup', JSON.stringify(respuestasGuardadas));
            console.log('Respuesta guardada localmente como respaldo');
        } catch (e) {
            console.error('Error al guardar localmente:', e);
        }
    }

    // Inicializar: ocultar todas las actividades primero
    actividades.forEach(actividad => {
        actividad.style.display = 'none';
    });

    // Mostrar solo la primera actividad
    if (actividades.length > 0) {
        mostrarActividad(0);
    } else {
        console.warn('No se encontraron actividades para mostrar');
    }

    // Agregar event listeners a los botones de "Siguiente" y "Ver Resultados"
    document.querySelectorAll('.btn-blue, .validar-imagenes').forEach(boton => {
        boton.addEventListener('click', function(event) {
            event.preventDefault();
            console.log('Botón clickeado:', this.textContent.trim(), this.name);

            // Validar la actividad actual antes de avanzar
            let actividadElement = null;

            if (actividades.length > actividadActual) {
                actividadElement = actividades[actividadActual];
            } else {
                console.error('Índice de actividad fuera de rango:', actividadActual);
            }

            const esValida = validarActividad(actividadElement);

            if (esValida) {
                // Si es la última actividad y el botón dice "Ver Resultados"
                if (actividadActual === totalActividades - 1 &&
                    (this.name === 'finish' || this.textContent.trim() === 'Ver Resultados')) {
                    console.log('Última actividad con botón de resultados, redirigiendo...');
                    dirigirAResultados();
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

    // Verificar si estamos en la página de resultados
    if (window.location.pathname.includes('result_form') || window.location.pathname.includes('results')) {
        console.log('Estamos en la página de resultados');
    }

    // Función de diagnóstico (puede ser llamada desde la consola del navegador)
    window.diagnosticarNavegacion = function() {
        console.log('=== DIAGNÓSTICO DE NAVEGACIÓN ===');
        console.log('Actividades encontradas:', actividades.length);
        console.log('Actividad actual:', actividadActual);
        console.log('Botones de navegación:', document.querySelectorAll('.btn-blue, .validar-imagenes').length);
        console.log('URL actual:', window.location.href);
        console.log('Pathname:', window.location.pathname);
        console.log('Respuestas locales:', localStorage.getItem('respuestas_backup'));
    };
});