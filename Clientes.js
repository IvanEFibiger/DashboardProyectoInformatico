document.addEventListener('DOMContentLoaded', function () {
  var links = document.querySelectorAll('a[data-target]');
  var mainContent = document.querySelector('main');

  links.forEach(function (link) {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      var targetFormId = link.getAttribute('data-target');
      var targetForm = document.getElementById(targetFormId);

      // Oculta todos los formularios y luego muestra el formulario deseado
      mainContent.querySelectorAll('form').forEach(function (form) {
        form.style.display = 'none';
      });

      targetForm.style.display = 'block';
    });
  });
});

document.addEventListener('DOMContentLoaded', function () {
  var mainContent = document.querySelector('main');
  var clientesListContainer = document.getElementById('clientesListContainer');

  // Function to show the clientesListContainer
  function showClientesList() {
    clientesListContainer.style.display = 'block';
  }

  // Function to hide the clientesListContainer
  function hideClientesList() {
    clientesListContainer.style.display = 'none';
  }

  // Initial setup - show the list when the page loads
  showClientesList();

  function linkClickHandler(event) {
    event.preventDefault();
    var targetFormId = this.getAttribute('data-target');

    // Check if the target form is 'listaClientes' (Clientes List)
    if (targetFormId === 'listaClientes') {
      showClientesList();
    } else {
      // For other sections, hide the list
      hideClientesList();
    }

    // Rest of your existing logic...
  }

  // Handling clicks on links
  var links = document.querySelectorAll('a[data-target]');
  links.forEach(function (link) {
    link.addEventListener('click', linkClickHandler);
  });

  // ... Rest of your existing code ...
});


//ALTA
// Espera a que el DOM esté cargado
document.addEventListener('DOMContentLoaded', function () {
  // Encuentra el enlace de "Alta"
  var altaLink = document.querySelector('a[data-target="altaForm"]');

  // Encuentra el formulario de Alta
  var altaForm = document.getElementById('altaClienteForm');

  // Agrega un evento de clic al enlace de "Alta"
  altaLink.addEventListener('click', function (event) {
    // Evita que se ejecute la acción predeterminada del enlace
    event.preventDefault();

    // Muestra el formulario de Alta
    altaForm.style.display = 'block';

    // agregar más lógica aquí,  ocultar otros elementos, etc.
  });
});


 // Espera a que el DOM esté cargado
 document.addEventListener('DOMContentLoaded', function () {
  // Encuentra el formulario de Alta
  var altaForm = document.getElementById('altaClienteForm');

  // Agrega un evento de envío al formulario
  altaForm.addEventListener('submit', function (event) {
      event.preventDefault(); // Evita que el formulario se envíe y la página se recargue

      // Lógica para guardar el cliente 

      // Muestra el mensaje de confirmación
      var mensajeClienteGuardado = document.getElementById('mensajeClienteGuardado');
      mensajeClienteGuardado.style.display = 'block';

      // ocultar el mensaje después de unos segundos 
      setTimeout(function () {
          mensajeClienteGuardado.style.display = 'none';
      }, 3000); // Oculta el mensaje después de 3 segundos 

      // Limpia los campos del formulario
      altaForm.reset();
  });
});

//MODIFICAR

// Espera a que el DOM esté cargado
document.addEventListener('DOMContentLoaded', function () {
  // Encuentra el enlace de "Modificar"
  var modificarLink = document.querySelector('a[data-target="modificarForm"]');

  // Encuentra el formulario de Modificación
  var modificarForm = document.getElementById('modificarClienteForm');

  // Agrega un evento de clic al enlace de "Modificar"
  modificarLink.addEventListener('click', function (event) {
      // Evita que se ejecute la acción predeterminada del enlace
      event.preventDefault();

      // Oculta el formulario de Alta (si está visible)
      var altaForm = document.getElementById('altaClienteForm');
      altaForm.style.display = 'none';

      // Muestra el formulario de Modificación
      modificarForm.style.display = 'block';

      // agregar más lógica aquí, como ocultar otros elementos, etc.
  });

  // Agrega un evento de envío al formulario de Modificación
  modificarForm.addEventListener('submit', function (event) {
      event.preventDefault(); // Evita que el formulario se envíe y la página se recargue

      // Lógica para guardar los cambios del cliente 

      // Muestra el mensaje de confirmación
      var mensajeClienteModificado = document.getElementById('mensajeClienteModificado');
      mensajeClienteModificado.style.display = 'block';

      // ocultar el mensaje después de unos segundos 
      setTimeout(function () {
          mensajeClienteModificado.style.display = 'none';
      }, 3000); // Oculta el mensaje después de 3 segundos 

      // Limpia los campos del formulario
      modificarForm.reset();
  });
});


//BAJA

document.addEventListener('DOMContentLoaded', function () {
  var bajaLink = document.querySelector('a[data-target="bajaForm"]');
  var bajaForm = document.getElementById('bajaClienteForm');

  bajaLink.addEventListener('click', function (event) {
    event.preventDefault();
    bajaForm.style.display = 'block';
    // agregar más lógica aquí, como ocultar otros elementos, etc.
  });
});


//facturas
document.addEventListener('DOMContentLoaded', function () {
  var facturasLink = document.querySelector('a[data-target="facturasForm"]');
  var facturasForm = document.getElementById('facturasForm');

  facturasLink.addEventListener('click', function (event) {
      event.preventDefault();
      facturasForm.style.display = 'block';

      // Oculta otros formularios si es necesario
      altaClienteForm.style.display = 'none';
      modificarClienteForm.style.display = 'none';
      bajaClienteForm.style.display = 'none';
  });
});


// SALDO
document.addEventListener('DOMContentLoaded', function () {
  var saldoLink = document.querySelector('a[data-target="saldoForm"]');
  var saldoForm = document.getElementById('saldoForm');

  saldoLink.addEventListener('click', function (event) {
      event.preventDefault();
      saldoForm.style.display = 'block';

      // Oculta otros formularios si es necesario
      altaClienteForm.style.display = 'none';
      modificarClienteForm.style.display = 'none';
      bajaClienteForm.style.display = 'none';
      facturasForm.style.display = 'none';
  });
});