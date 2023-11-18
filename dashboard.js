  // mostrar/ocultar el "Dashboard"
$(document).ready(function () {
  // Agrega un evento de clic a la pestaña "Dashboard"
  $('.nav-link[href="#mobileMenu"]').on('click', function () {
      // Alterna el estado del menú desplegable
      $('#mobileMenu').offcanvas('toggle');
  });
});

//nombre de usuario del dashboard

// Supongamos que obtienes el nombre de usuario de alguna manera, por ejemplo, de una variable llamada 'nombreUsuario'
var nombreUsuario = "UsuarioEjemplo";

// Actualiza el contenido del span con el ID 'usernamePlaceholder'
document.getElementById("usernamePlaceholder").textContent = nombreUsuario;