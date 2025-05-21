/*Parte del pentágono*/
document.querySelectorAll("#mapa svg path").forEach((path) => {
    path.addEventListener('click', function () {
        const url = this.getAttribute('data-url');
        if (url) {
            window.location.href = url;
        }
    });
});

// Actividad de selección
document.addEventListener('DOMContentLoaded', () => {
  const imageItems = document.querySelectorAll('.image-item');
  const checkButton = document.getElementById('checkAnswers');
  const resultDiv = document.getElementById('result');
  const selected = new Set();
  const correctImageIds = [1, 4];
  const MAX_SELECTIONS = 2;

  imageItems.forEach(item => {
    item.addEventListener('click', () => {
      const value = item.getAttribute('data-value');

      if (selected.has(value)) {
        selected.delete(value);
        item.classList.remove('selected');
      } else if (selected.size < MAX_SELECTIONS) {
        selected.add(value);
        item.classList.add('selected');
      } else {
        alert('Solo puedes seleccionar dos imágenes.');
      }
    });
  });

  checkButton?.addEventListener('click', () => {
    const selectedImages = document.querySelectorAll('.image-item.selected');
    const selectedIds = Array.from(selectedImages).map(item => parseInt(item.dataset.id));

    if (selectedIds.length !== MAX_SELECTIONS) {
      resultDiv.innerHTML = '<div class="alert alert-warning">Debes seleccionar exactamente 2 imágenes.</div>';
      return;
    }

    const isCorrect = correctImageIds.every(id => selectedIds.includes(id)) &&
                     selectedIds.every(id => correctImageIds.includes(id));

    fetch('/guardar_respuesta/', {
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
        subtopic_id: parseInt(document.querySelector('.actividad').dataset.subtopicId)
      })
    })
    .then(response => response.json())
    .then(data => console.log('Respuesta guardada:', data))
    .catch(error => console.error('Error al enviar al backend:', error));
  });
});

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

    fetch('/guardar_respuesta/', {
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
            subtopic_id: parseInt(document.querySelector('.actividad').dataset.subtopicId)
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

/* Actividad responder */
document.addEventListener('DOMContentLoaded', function () {
    const respuestasInputs = document.querySelectorAll('.respuesta-input');
    respuestasInputs.forEach(inputRespuesta => {
        inputRespuesta.addEventListener('blur', function () {
            const respuestaUsuario = this.value.trim().toLowerCase();
            const posiblesRespuestas = this.dataset.respuesta.split(',').map(r => r.trim().toLowerCase());
            const esCorrecta = posiblesRespuestas.includes(respuestaUsuario);

            fetch('/guardar_respuesta/', {
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
});
