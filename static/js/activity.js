/*Parte del pentágono*/
document.querySelectorAll("#mapa svg path").forEach((path) => {
    path.addEventListener('click', function () {
        const url = this.getAttribute('data-url');
        if (url) {
            window.location.href = url;
        }
    });
});

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

// Actividad de selección
document.addEventListener('DOMContentLoaded', function () {
    const imageItems = document.querySelectorAll('.image-item');
    const checkButton = document.getElementById('checkAnswers');
    const resultDiv = document.getElementById('result');
    const selected = new Set();

    const correctImageIds = [1, 4];

    imageItems.forEach(item => {
        item.addEventListener('click', function () {
            const value = this.getAttribute('data-value');

            if (selected.has(value)) {
                selected.delete(value);
                this.classList.remove('selected');
            } else {
                if (selected.size < 2) {
                    selected.add(value);
                    this.classList.add('selected');
                } else {
                    alert('Solo puedes seleccionar dos imágenes.');
                }
            }
        });
    });

    if (checkButton) {
        checkButton.addEventListener('click', function () {
            const selectedImages = document.querySelectorAll('.image-item.selected');
            const selectedIds = Array.from(selectedImages).map(item => parseInt(item.dataset.id));

            if (selectedIds.length !== 2) {
                resultDiv.innerHTML = '<div class="alert alert-warning">Debes seleccionar exactamente 2 imágenes.</div>';
                return;
            }

            let isCorrect = correctImageIds.every(id => selectedIds.includes(id)) &&
                selectedIds.every(id => correctImageIds.includes(id));

            resultDiv.innerHTML = isCorrect
                ? '<div class="alert alert-success">¡Correcto!</div>'
                : '<div class="alert alert-danger">Incorrecto. Inténtalo nuevamente.</div>';

            // Guardar respuesta y copia local
            const respuestaData = {
                selected_ids: selectedIds,
                is_correct: isCorrect,
                activity_type: 'seleccion_imagenes',
                activity_id: 1,
                subtopic_id: parseInt(document.querySelector('.actividad').dataset.subtopicId)
            };

            // Guardar copia local por seguridad
            guardarRespuestaLocal(respuestaData);

            fetch('/guardar_respuesta/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(respuestaData)
            })
                .then(response => response.json())
                .then(data => {
                    console.log('Respuesta guardada:', data);
                })
                .catch(error => {
                    console.error('Error al enviar al backend:', error);
                });
        });
    }
});

// Función para guardar respuesta localmente como respaldo
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

/*Actividad espacios en blanco*/
const blanks = document.querySelectorAll('.blank');
blanks.forEach(blank => {
    const input = document.createElement('input');
    blank.appendChild(input);
});

function verificarRespuestas() {
    const blanks = document.querySelectorAll('.blank');
    let todasCorrectas = true;
    const resultados = [];

    blanks.forEach((blank, index) => {
        const input = blank.querySelector('input');
        const respuestaUsuario = input ? input.value.trim().toLowerCase() : "";
        const respuestasCorrectas = blank.dataset.respuesta.split(',').map(r => r.trim().toLowerCase());
        const esCorrecta = respuestasCorrectas.includes(respuestaUsuario);

        if (!esCorrecta) todasCorrectas = false;

        resultados.push({
            index: index,
            respuesta_usuario: respuestaUsuario,
            respuestas_correctas: respuestasCorrectas,
            es_correcta: esCorrecta
        });
    });

    // Datos para enviar al servidor
    const datosRespuesta = {
        activity_type: 'espacios_blanco',
        activity_id: 1,
        user_response: resultados,
        is_correct: todasCorrectas,
        subtopic_id: parseInt(document.querySelector('.actividad').dataset.subtopicId)
    };

    // Guardar copia local por seguridad
    guardarRespuestaLocal(datosRespuesta);

    fetch('/guardar_respuesta/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(datosRespuesta)
    })
        .then(response => response.json())
        .then(data => {
            console.log('Respuesta guardada:', data);
        })
        .catch(error => {
            console.error('Error al enviar al backend:', error);
        });
}

/* Actividad responder */
document.addEventListener('DOMContentLoaded', function () {
    const respuestasInputs = document.querySelectorAll('.respuesta-input');
    respuestasInputs.forEach(inputRespuesta => {
        inputRespuesta.addEventListener('blur', function () {
            const respuestaUsuario = this.value.trim().toLowerCase();
            const posiblesRespuestas = this.dataset.respuesta.split(',').map(r => r.trim().toLowerCase());
            const esCorrecta = posiblesRespuestas.includes(respuestaUsuario);

            // Datos para enviar al servidor
            const datosRespuesta = {
                activity_type: 'respuesta_libre',
                activity_id: parseInt(this.closest('.actividad').dataset.preguntaId),
                user_response: respuestaUsuario,
                is_correct: esCorrecta,
                subtopic_id: parseInt(this.closest('.actividad').dataset.subtopicId)
            };

            // Guardar copia local por seguridad
            guardarRespuestaLocal(datosRespuesta);

            fetch('/guardar_respuesta/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(datosRespuesta)
            })
                .then(response => response.json())
                .then(data => {
                    console.log('Respuesta enviada:', data);
                })
                .catch(error => {
                    console.error('Error al enviar al backend:', error);
                });
        });
    });
});

// Función para mostrar un mensaje si las respuestas no se cargan
function mostrarModalInfo(titulo, mensaje) {
    // Crear el modal
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'infoModal';
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-labelledby', 'infoModalLabel');
    modal.setAttribute('aria-hidden', 'true');

    modal.innerHTML = `
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="infoModalLabel">${titulo}</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    ${mensaje}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary" data-dismiss="modal">Entendido</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Mostrar el modal usando jQuery si está disponible, o manualmente si no
    if (typeof $ !== 'undefined') {
        $('#infoModal').modal('show');
    } else {
        modal.style.display = 'block';
        modal.style.backgroundColor = 'rgba(0,0,0,0.5)';

        // Agregar evento de cierre al botón
        modal.querySelector('button[data-dismiss="modal"]').addEventListener('click', function() {
            document.body.removeChild(modal);
        });
    }
}

// Verificar si estamos en la página de resultados y no hay datos
document.addEventListener('DOMContentLoaded', function() {
    // Si estamos en la página de resultados
    if (window.location.pathname.includes('result_form') || window.location.pathname.includes('results')) {
        const questionCards = document.querySelectorAll('.question-card');

        // Si no hay tarjetas de preguntas, mostrar el botón para recuperar respuestas locales
        if (questionCards.length === 0) {
            const container = document.querySelector('.container .card-body');
            if (container) {
                const btnRecuperar = document.createElement('button');
                btnRecuperar.className = 'btn btn-warning mt-3';
                btnRecuperar.textContent = 'Recuperar respuestas del almacenamiento local';
                btnRecuperar.onclick = mostrarRespuestasLocales;

                const mensaje = document.createElement('div');
                mensaje.className = 'alert alert-info mt-3';
                mensaje.textContent = 'No se encontraron respuestas en el servidor. Puedes intentar recuperarlas del almacenamiento local.';

                container.appendChild(mensaje);
                container.appendChild(btnRecuperar);
            }
        }
    }
});

// Función para mostrar respuestas del almacenamiento local
function mostrarRespuestasLocales() {
    try {
        const respuestasLocales = JSON.parse(localStorage.getItem('respuestas_backup')) || [];

        if (respuestasLocales.length === 0) {
            mostrarModalInfo('Sin datos locales', 'No se encontraron respuestas guardadas en el almacenamiento local.');
            return;
        }

        const container = document.querySelector('.container .card-body');
        if (!container) return;

        // Crear un contenedor para las respuestas
        const respuestasDiv = document.createElement('div');
        respuestasDiv.className = 'mt-4';
        respuestasDiv.innerHTML = '<h4>Respuestas recuperadas del almacenamiento local:</h4>';

        // Mostrar cada respuesta
        respuestasLocales.forEach((item, index) => {
            const fecha = new Date(item.timestamp).toLocaleString();
            const datos = item.datos;

            let respuestaMostrada = '';
            if (datos.user_response) {
                if (Array.isArray(datos.user_response)) {
                    respuestaMostrada = datos.user_response.join(', ');
                } else {
                    respuestaMostrada = datos.user_response;
                }
            } else if (datos.selected_ids) {
                respuestaMostrada = datos.selected_ids.join(', ');
            }

            const respuestaCard = document.createElement('div');
            respuestaCard.className = `question-card ${datos.is_correct ? 'correct' : 'incorrect'}`;
            respuestaCard.innerHTML = `
                <p><strong>Actividad ${index + 1}</strong></p>
                <p>Tipo: ${datos.activity_type}</p>
                <p>Tu respuesta: ${respuestaMostrada}</p>
                <p>Resultado: ${datos.is_correct ? 'Correcto' : 'Incorrecto'}</p>
                <p><small>Guardado: ${fecha}</small></p>
            `;

            respuestasDiv.appendChild(respuestaCard);
        });

        // Si ya existe un contenedor de respuestas locales, reemplazarlo
        const existingContainer = document.getElementById('respuestas-locales');
        if (existingContainer) {
            existingContainer.parentNode.removeChild(existingContainer);
        }

        respuestasDiv.id = 'respuestas-locales';
        container.appendChild(respuestasDiv);
    } catch (e) {
        console.error('Error al mostrar respuestas locales:', e);
        mostrarModalInfo('Error', 'Ocurrió un error al intentar recuperar las respuestas locales.');
    }
}