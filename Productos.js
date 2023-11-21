document.addEventListener('DOMContentLoaded', function () {
  // Función para mostrar un formulario y ocultar los demás
  function showForm(targetFormId) {
    // Oculta todos los formularios
    mainContent.querySelectorAll('form').forEach(function (form) {
      form.style.display = 'none';
    });

    // Muestra el formulario deseado
    var targetForm = document.getElementById(targetFormId);
    targetForm.style.display = 'block';
  }

  // Función para mostrar la lista de productos
  function showProdList() {
    prodListContainer.style.display = 'block';
  }

  // Función para ocultar la lista de productos
  function hideProdList() {
    prodListContainer.style.display = 'none';
  }

  // Obtener elementos principales
  var mainContent = document.querySelector('main');
  var prodListContainer = document.getElementById('prodListContainer');

  // Lista de enlaces con atributo data-target
  var links = document.querySelectorAll('a[data-target]');

  // Manejador de clics en enlaces
  links.forEach(function (link) {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      var targetFormId = link.getAttribute('data-target');

      // Mostrar u ocultar la lista de productos según sea necesario
      if (targetFormId === 'listaProductos') {
        showProdList();
      } else {
        hideProdList();
      }

      // Mostrar el formulario correspondiente
      showForm(targetFormId);
    });
  });

  // Alta de productos
  var altaProdForm = document.getElementById('altaProdForm');
  var altaLink = document.querySelector('a[data-target="altaProdForm"]');

  altaLink.addEventListener('click', function (event) {
    event.preventDefault();
    showForm('altaProdForm');
  });

  altaProdForm.addEventListener('submit', function (event) {
    event.preventDefault();
    // Lógica para guardar el producto

    // Mostrar mensaje de confirmación
    var mensajeProdGuardado = document.getElementById('mensajeProductoGuardado');
    mensajeProdGuardado.style.display = 'block';

    setTimeout(function () {
      mensajeProdGuardado.style.display = 'none';
    }, 3000);

    altaProdForm.reset();
  });

  // Modificar productos
  var modificarProdForm = document.getElementById('modificarProdForm');
  var modificarProdLink = document.querySelector('a[data-target="modificarProdForm"]');

  modificarProdLink.addEventListener('click', function (event) {
    event.preventDefault();

    // Oculta el formulario de Alta de Producto (si está visible)
    var altaProdForm = document.getElementById('altaProdForm');
    altaProdForm.style.display = 'none';

    showForm('modificarProdForm');
  });

  modificarProdForm.addEventListener('submit', function (event) {
    event.preventDefault();
    // Lógica para guardar los cambios del producto 

    // Muestra el mensaje de confirmación
    var mensajeProdModificado = document.getElementById('mensajeClienteModificado');
    mensajeProdModificado.style.display = 'block';

    setTimeout(function () {
      mensajeProdModificado.style.display = 'none';
    }, 3000);

    modificarProdForm.reset();
  });
});
