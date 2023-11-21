document.addEventListener('DOMContentLoaded', function () {
  // Variables globales
  var links = document.querySelectorAll('a[data-target]');
  var mainContent = document.querySelector('main');
  var serviciosListContainer = document.getElementById('sevicListContainer');

  // Funciones de visualización y ocultación de la lista de servicios
  function showServiciosList() {
    serviciosListContainer.style.display = 'block';
  }

  function hideServiciosList() {
    serviciosListContainer.style.display = 'none';
  }

  // Función para manejar clics en enlaces
  function linkClickHandler(event) {
    event.preventDefault();
    var targetFormId = this.getAttribute('data-target');

    // Verifica si el formulario de destino es 'listaServicios' (Lista de Servicios)
    if (targetFormId === 'listaServicios') {
      showServiciosList();
    } else {
      // Para otras secciones, oculta la lista
      hideServiciosList();
    }

    // Oculta todos los formularios y luego muestra el formulario deseado
    mainContent.querySelectorAll('form').forEach(function (form) {
      form.style.display = 'none';
    });

    var targetForm = document.getElementById(targetFormId);
    targetForm.style.display = 'block';
  }

  // Manejo de clics en enlaces
  links.forEach(function (link) {
    link.addEventListener('click', linkClickHandler);
  });

  // ... Resto de tu código ...

  // ALTA de servicios
  var altaLink = document.querySelector('a[data-target="altaServiForm"]');
  var altaServiForm = document.getElementById('altaServicForm');

  altaLink.addEventListener('click', function (event) {
    event.preventDefault();
    altaServiForm.style.display = 'block';
  });

  altaServiForm.addEventListener('submit', function (event) {
    event.preventDefault();
    // Lógica para guardar el servicio
    var mensajeServicioGuardado = document.getElementById('mensajeServicioGuardado');
    mensajeServicioGuardado.style.display = 'block';

    setTimeout(function () {
      mensajeServicioGuardado.style.display = 'none';
    }, 3000);

    altaServiForm.reset();
  });

  // MODIFICAR servicios
  var modificarLink = document.querySelector('a[data-target="modificarServiForm"]');
  var modificarServiForm = document.getElementById('modificarServiceForm');

  modificarLink.addEventListener('click', function (event) {
    event.preventDefault();
    var altaServiForm = document.getElementById('altaServicForm');
    altaServiForm.style.display = 'none';
    modificarServiForm.style.display = 'block';
  });

  modificarServiForm.addEventListener('submit', function (event) {
    event.preventDefault();
    // Lógica para guardar los cambios del servicio
    var mensajeServicioModificado = document.getElementById('mensajeServicModificado');
    mensajeServicioModificado.style.display = 'block';

    setTimeout(function () {
      mensajeServicioModificado.style.display = 'none';
    }, 3000);

    modificarServiForm.reset();
  });
});
