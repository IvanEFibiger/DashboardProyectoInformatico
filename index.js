
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


// Login

var loginLink = document.getElementById("loginLink");
var loginPopup = document.getElementById("loginPopup");
var closePopup = document.getElementById("closePopup");
var loginForm = document.getElementById("loginForm");

// Abre el popup al hacer clic en el enlace
loginLink.addEventListener("click", function(e) {
  e.preventDefault();
  loginPopup.style.display = "block";
});

// Cierra el popup al hacer clic en el botón de cierre
closePopup.addEventListener("click", function() {
  loginPopup.style.display = "none";
});

// Cierra el popup al hacer clic fuera del contenido
window.addEventListener("click", function(event) {
  if (event.target === loginPopup) {
    loginPopup.style.display = "none";
  }
});

// Evita que el evento de clic se propague desde el formulario al contenedor
loginForm.addEventListener("click", function(event) {
  event.stopPropagation();
});

// Puedes agregar código para procesar el inicio de sesión aquí
