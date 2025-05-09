
/*Parte del pentagono*/
document.querySelectorAll("#mapa svg path").forEach((path) => {
    path.addEventListener('click', function () {
        const url = this.getAttribute('data-url');
        if (url) {
            window.location.href = url;
        }
    });
});

//Actividad de seleccion
document.addEventListener('DOMContentLoaded', function () {
    const imageItems = document.querySelectorAll('.image-item');
    const checkButton = document.getElementById('checkAnswers');
    const resultDiv = document.getElementById('result');
    const selected = new Set();

    const correctImageIds = [1, 4]; // Esto puede venir de Django también

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

        fetch('/guardar-respuesta/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                selected_ids: selectedIds,
                is_correct: isCorrect,
                activity_type: 'seleccion_imagenes',
                activity_id: 1, 
                subtopic_id: parseInt(this.closest('.actividad').dataset.subtopicId)
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Respuesta guardada:', data);
        })
        .catch(error => {
            console.error('Error al enviar al backend:', error);
        });
    });
});


/*Actividad espacios en blanco*/

// Añadir inputs a los spans
const blanks = document.querySelectorAll('.blank');
blanks.forEach(blank => {
    const input = document.createElement('input');
    blank.appendChild(input);
});

function verificarRespuestas() {
    const blanks = document.querySelectorAll('.blank');
    let todasCorrectas = true;
    const resultados = [];

    blanks.forEach(blank => {
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

    fetch('/guardar-respuesta/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            activity_type: 'espacios_blanco',
            activity_id: 1,
            user_response: resultados,
            is_correct: todasCorrectas,
            subtopic_id: parseInt(this.closest('.actividad').dataset.subtopicId)            
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Respuesta guardada:', data);
    })
    .catch(error => {
        console.error('Error al enviar al backend:', error);
    });


}

/* Actividad Arrastrar y soltar*/

const container = document.getElementById('stepsContainer');
let draggedItem = null;

container.addEventListener('dragstart', e => {
    if (e.target.classList.contains('step')) {
        draggedItem = e.target;
        e.target.classList.add('dragging');
    }
});

container.addEventListener('dragend', e => {
    if (draggedItem) {
        draggedItem.classList.remove('dragging');
        draggedItem = null;
    }
});

container.addEventListener('dragover', e => {
    e.preventDefault();
    const afterElement = getDragAfterElement(container, e.clientY);
    if (afterElement == null) {
        container.appendChild(draggedItem);
    } else {
        container.insertBefore(draggedItem, afterElement);
    }
});

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.step:not(.dragging)')];
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset) {
            return {offset: offset, element: child};
        } else {
            return closest;
        }
    }, {offset: Number.NEGATIVE_INFINITY}).element;
}

function verificarOrden() {
    const contenedor = document.getElementById('stepsContainer');
    const elementos = contenedor.querySelectorAll('.step');

    const respuestaUsuario = Array.from(elementos).map(el => parseInt(el.dataset.index));
    const respuestasCorrectas = contenedor.dataset.respuesta.split(',').map(n => parseInt(n.trim()));
    const esCorrecta = JSON.stringify(respuestaUsuario) === JSON.stringify(respuestasCorrectas);

    fetch('/guardar-respuesta/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            activity_type: 'arrastrar_soltar',
            activity_id: 2,
            user_response: respuestaUsuario,
            is_correct: esCorrecta,
            subtopic_id: parseInt(this.closest('.actividad').dataset.subtopicId)
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Orden enviado:', data);
    })
    .catch(error => {
        console.error('Error al enviar al backend:', error);
    });
}

/* Actividad responder*/

document.addEventListener('DOMContentLoaded', function() {
    const respuestasInputs = document.querySelectorAll('.respuesta-input');
    
    inputRespuesta.addEventListener('blur', function() {
        const respuestaUsuario = this.value.trim().toLowerCase();
            const posiblesRespuestas = this.dataset.respuesta.split(',').map(r => r.trim().toLowerCase());
            const esCorrecta = posiblesRespuestas.includes(respuestaUsuario);
        
        fetch('/guardar-respuesta/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                activity_type: 'respuesta_libre',
                activity_id: parseInt(this.closest('.actividad').dataset.preguntaId),
                user_response: respuestaUsuario,
                is_correct: esCorrecta,
                subtopic_id: parseInt(this.closest('.actividad').dataset.subtopicId)
            })
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

/* Actividad de seleccionar*/

document.addEventListener('DOMContentLoaded', function() {
    // Manejo de <select>
    document.querySelectorAll('.actividad select').forEach(select => {
        select.addEventListener('change', function () {
            const respuestaCorrecta = this.dataset.respuesta;
            const valorSeleccionado = this.value;
            const esCorrecta = valorSeleccionado === respuestaCorrecta;

            fetch('/guardar-respuesta/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    activity_type: 'seleccion_opcion',
                    activity_id: parseInt(this.closest('.actividad').dataset.preguntaId),
                    user_response: valorSeleccionado,
                    is_correct: esCorrecta,
                    subtopic_id: parseInt(this.closest('.actividad').dataset.subtopicId)
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Respuesta de select enviada:', data);
            })
            .catch(error => {
                console.error('Error al enviar select:', error);
            });
        });
    });

    // Manejo de <input type="radio">
    document.querySelectorAll('.actividad input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function () {
            const esCorrecta = this.dataset.respuesta === "true";

            fetch('/guardar-respuesta/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    activity_type: 'seleccion_opcion',
                    activity_id: parseInt(this.closest('.actividad').dataset.preguntaId),
                    user_response: this.nextElementSibling.innerText.trim(),
                    is_correct: esCorrecta,
                    subtopic_id: parseInt(this.closest('.actividad').dataset.subtopicId)
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Respuesta de radio enviada:', data);
            })
            .catch(error => {
                console.error('Error al enviar radio:', error);
            });
        });
    });
});
