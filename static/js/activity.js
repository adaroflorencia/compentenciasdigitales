//Actividad de seleccionar
document.addEventListener('DOMContentLoaded', () => {
  const imageItems = document.querySelectorAll('.image-item');
  const submitButton = document.querySelector('.validar-imagenes');
  const MAX_SELECTIONS = 2;
  let selectedImages = [];

  function toggleSelection(element) {
    const imageId = element.dataset.id || selectedImages.length + 1; // Usar data-id si existe, sino generar uno
    const isSelected = element.classList.contains('selected');

    if (isSelected) {
      // Deseleccionar imagen
      element.classList.remove('selected');
      element.style.backgroundColor = '';
      element.style.border = '';
      element.style.transform = '';
      element.style.boxShadow = '';

      const overlay = element.querySelector('.selection-overlay');
      if (overlay) overlay.style.display = 'none';

      // Remover de array de seleccionadas
      selectedImages = selectedImages.filter(id => id !== imageId);

      // Desmarcar radio button si existe
      const radioInput = element.querySelector('input[type="radio"]');
      if (radioInput) radioInput.checked = false;

    } else {
      // Verificar límite de selecciones
      if (selectedImages.length >= MAX_SELECTIONS) {
        alert(`Solo puedes seleccionar ${MAX_SELECTIONS} imágenes máximo`);
        return;
      }

      // Seleccionar imagen con efectos visuales
      element.classList.add('selected');
      element.style.backgroundColor = 'rgba(0, 123, 255, 0.15)';
      element.style.border = '3px solid #007bff';
      element.style.transform = 'scale(1.02)';
      element.style.boxShadow = '0 4px 15px rgba(0, 123, 255, 0.3)';
      element.style.transition = 'all 0.3s ease';

      // Mostrar overlay si existe
      const overlay = element.querySelector('.selection-overlay');
      if (overlay) {
        overlay.style.display = 'block';
        overlay.style.backgroundColor = 'rgba(0, 123, 255, 0.2)';
        overlay.style.border = '2px solid #007bff';
      }

      // Agregar a array de seleccionadas
      selectedImages.push(imageId);

      // Marcar radio button si existe (para compatibilidad)
      const radioInput = element.querySelector('input[type="radio"]');
      if (radioInput) radioInput.checked = true;
    }

    // Actualizar contador si existe
    const contador = document.getElementById('contador-selecciones');
    if (contador) {
      contador.textContent = selectedImages.length;
    }

    // Actualizar campo oculto si existe
    const hiddenInput = document.getElementById('selected_images');
    if (hiddenInput) {
      hiddenInput.value = selectedImages.join(',');
    }

    console.log('Imágenes seleccionadas:', selectedImages);
  }

  // Asignar evento de clic a cada imagen
  imageItems.forEach((item, index) => {
    // Asignar data-id si no existe
    if (!item.dataset.id) {
      item.dataset.id = index + 1;
    }

    item.addEventListener('click', (e) => {
      e.preventDefault();
      toggleSelection(item);
    });
  });

  // Validar antes de enviar
  submitButton?.addEventListener('click', (e) => {
    if (selectedImages.length === 0) {
      e.preventDefault();
      alert('Debes seleccionar al menos una imagen antes de continuar.');
      return;
    }

    if (selectedImages.length > MAX_SELECTIONS) {
      e.preventDefault();
      alert(`Solo puedes seleccionar máximo ${MAX_SELECTIONS} imágenes.`);
      return;
    }

    console.log('Enviando selecciones:', selectedImages);
  });
});

/*Actividad input*/

document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');

  // Función para convertir texto a Title Case
  function toTitleCase(str) {
    return str.toLowerCase().split(' ').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  }

  // Validación al enviar el formulario
  form?.addEventListener('submit', (e) => {
    const textInputs = form.querySelectorAll('input[type="text"], textarea');

    // Formatear todos los campos de texto
    textInputs.forEach(input => {
      if (input.value && input.value.trim() !== '') {
        input.value = toTitleCase(input.value.trim());
      }
    });
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