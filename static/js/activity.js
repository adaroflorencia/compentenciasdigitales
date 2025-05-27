//Actividad de seleccionar
document.addEventListener('DOMContentLoaded', () => {
  const imageItems = document.querySelectorAll('.image-item');
  const checkButton = document.getElementById('checkAnswers');
  const resultDiv = document.getElementById('result');
  const contadorSpan = document.getElementById('contador-selecciones');
  const correctImageIds = [1, 4];
  const MAX_SELECTIONS = 2;
  let selecciones = [];

  function toggleSeleccion(element, imagenId) {
    const overlay = element.querySelector('.selection-overlay');

    if (element.classList.contains('selected')) {
      // Deseleccionar
      element.classList.remove('selected');
      selecciones = selecciones.filter(id => id !== imagenId);
      if (overlay) overlay.style.display = 'none';
    } else {
      if (selecciones.length >= MAX_SELECTIONS) {
        alert('Solo puedes seleccionar 2 imágenes');
        return;
      }
      // Seleccionar
      element.classList.add('selected');
      selecciones.push(imagenId);
      if (overlay) overlay.style.display = 'block';
    }

    // Actualizar contador y campo oculto
    contadorSpan.textContent = selecciones.length;
    const hiddenInput = document.getElementById('selected_images');
    if (hiddenInput) hiddenInput.value = selecciones.join(',');
  }

  // Asignar evento de clic a cada imagen
  imageItems.forEach(item => {
    const imagenId = parseInt(item.dataset.id);
    item.addEventListener('click', () => toggleSeleccion(item, imagenId));
  });

  // Enviar respuestas al backend
  checkButton?.addEventListener('click', () => {
    if (selecciones.length !== MAX_SELECTIONS) {
      resultDiv.innerHTML = '<div class="alert alert-warning">Debes seleccionar exactamente 2 imágenes.</div>';
      return;
    }

    const isCorrect = correctImageIds.every(id => selecciones.includes(id)) &&
                      selecciones.every(id => correctImageIds.includes(id));

    fetch('/guardar_respuesta/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({
        selected_ids: selecciones,
        is_correct: isCorrect,
        activity_type: 'seleccion_imagenes',
        activity_id: 1,
        subtopic_id: parseInt(document.querySelector('.actividad').dataset.subtopicId)
      })
    })
    .then(response => response.json())
    .then(data => {
      console.log('Respuesta guardada:', data);
    })
    .catch(error => console.error('Error al enviar al backend:', error));
  });
});

/*Actividad input*/

document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.querySelectorAll('')

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