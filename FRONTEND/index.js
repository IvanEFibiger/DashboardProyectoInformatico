
// BOTON ARRIBA
var scrollToTopBtn = document.getElementById("scrollToTopBtn");

var scrollToTopBtn = document.getElementById("scrollToTopBtn");
var isScrolling = false;
var scrollingTimer; // Variable para el temporizador

// Muestra el botón cuando el usuario ha desplazado
window.addEventListener("scroll", function() {
  if (!isScrolling) {
    isScrolling = true;
    scrollToTopBtn.style.display = "block";
  }

  clearTimeout(scrollingTimer); // Reinicia el temporizador
  scrollingTimer = setTimeout(function() {
    isScrolling = false;
    scrollToTopBtn.style.display = "none";
  }, 1500); 
});

// Haz scroll suave al principio de la página cuando se hace clic en el botón
scrollToTopBtn.addEventListener("click", function() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
});


