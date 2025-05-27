/*Partes del pentágono*/
document.querySelectorAll("#mapa svg path").forEach((path) => {
    path.addEventListener('click', function () {
        const url = this.getAttribute('data-url');
        if (url) {
            window.location.href = url;
        }
    });
});