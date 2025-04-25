document.addEventListener('DOMContentLoaded', function() {
        const imageItems = document.querySelectorAll('.image-item');
        const checkButton = document.getElementById('checkAnswers');
        const resultDiv = document.getElementById('result');

        const correctImageIds = [1, 4];
        
        imageItems.forEach(item => {
            item.addEventListener('click', function() {

                if (!item.classList.contains('correct') && !item.classList.contains('incorrect')) {
                    this.classList.toggle('selected');
                }
            });
        });
        
        checkButton.addEventListener('click', function() {
            const selectedImages = document.querySelectorAll('.image-item.selected');
            const selectedIds = Array.from(selectedImages).map(item => parseInt(item.dataset.id));
            

            let isCorrect = true;

            if (selectedIds.length !== 2) {
                resultDiv.innerHTML = '<div class="alert alert-warning">Debes seleccionar exactamente 2 imágenes.</div>';
                return;
            }

            if (!correctImageIds.every(id => selectedIds.includes(id)) || 
                !selectedIds.every(id => correctImageIds.includes(id))) {
                isCorrect = false;
            }
            

            if (isCorrect) {
                resultDiv.innerHTML = '<div class="alert alert-success">¡Correcto! Has seleccionado las imágenes correctas.</div>';
            } else {
                resultDiv.innerHTML = '<div class="alert alert-danger">Incorrecto. Inténtalo de nuevo.</div>';
            }
            

            imageItems.forEach(item => {
                const id = parseInt(item.dataset.id);
                
                if (correctImageIds.includes(id)) {
                    item.classList.add('correct');
                } else if (selectedIds.includes(id)) {
                    item.classList.add('incorrect');
                }
            });
        });
    });