// Llama a esta función para obtener y mostrar los datos de clientes paginados
function obtenerClientesPaginados(page) {
  const url = `http://127.0.0.1:5500/usuarios/${userId}/clientes-paginados?page=${page}`;

  $.ajax({
    url: url,
    type: 'GET',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    success: function (data) {
      // Limpia el cuerpo de la tabla
      $('#clientesTableBody').empty();

      // Itera sobre los datos y agrega filas a la tabla
      data.clients.forEach(function (cliente) {
        const row = `<tr>
                       <td>${cliente.cliente_id}</td>
                       <td>${cliente.nombre}</td>
                       <td>${cliente.direccion}</td>
                       <td>${cliente.email}</td>
                       <td>${cliente.cuit}</td>
                       <td>
                       <button class="btn btn-primary btn-edit" data-client-id="${cliente.cliente_id}">Editar</button>
                       <button class="btn btn-danger btn-delete" data-client-id="${cliente.cliente_id}">Eliminar</button>
                       </td>
                     </tr>`;
        $('#clientesTableBody').append(row);
      });

      // Actualiza la paginación
      actualizarPaginacion(data.total_pages, data.current_page);
    },
    error: function (error) {
      console.error('Error al obtener clientes paginados:', error);
    }
  });
}

function actualizarPaginacion(totalPages, currentPage) {
  // Elimina los elementos actuales de la paginación
  $('.pagination').empty();

  // Agrega el botón "Anterior"
  const prevButton = $('<li class="page-item"></li>');
  const prevLink = $(`<a class="page-link" href="#" data-page="${currentPage - 1}">Anterior</a>`);
  prevButton.append(prevLink);
  $('.pagination').append(prevButton);

  // Agrega el botón "Siguiente"
  const nextButton = $('<li class="page-item"></li>');
  const nextLink = $(`<a class="page-link" href="#" data-page="${currentPage + 1}">Siguiente</a>`);
  nextButton.append(nextLink);
  $('.pagination').append(nextButton);
}

// Llama a esta función para inicializar la tabla con la primera página de clientes
function inicializarTabla() {
  obtenerClientesPaginados(1);
}

$('.pagination').on('click', 'a.page-link', function (event) {
  event.preventDefault(); // Evita que el enlace recargue la página

  // Obtén el número de página desde el atributo data-page
  const page = $(this).data('page');

  // Llama a la función cambiarPagina con el número de página
  cambiarPagina(page);
});





// Evento de clic para el botón "Editar"
// Evento de clic para el botón "Editar"
$('#clientesTableBody').on('click', '.btn-edit', function () {
  const clientId = $(this).data('client-id');

  // Realiza una solicitud AJAX para obtener los detalles del cliente
  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/clientes/${clientId}`,
    type: 'GET',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    success: function (cliente) {
      // Muestra un pop-up con el formulario de edición
      mostrarFormularioEdicion(cliente);
    },
    error: function (error) {
      console.error('Error al obtener detalles del cliente:', error);
    }
  });
});

// Función para mostrar el pop-up con el formulario de edición
function mostrarFormularioEdicion(cliente) {
  // Llena los campos del formulario con los datos del cliente
  $('#nombre').val(cliente.nombre);
  $('#email').val(cliente.email);
  $('#direccion').val(cliente.direccion);
  $('#cuit').val(cliente.cuit);

  // Almacena el ID del cliente en un atributo de datos del botón "Guardar Cambios"
  $('#guardarCambiosCliente').data('client-id', cliente.cliente_id);

  // Muestra el modal
  $('#editarClienteModal').modal('show');
}

// Evento de clic para el botón "Guardar Cambios"
$('#guardarCambiosCliente').on('click', function () {
  // Obtén el ID del cliente almacenado en el atributo de datos del botón
  const clientId = $(this).data('client-id');

  // Obtén los valores actualizados del formulario
  const nombre = $('#nombre').val();
  const email = $('#email').val();
  const direccion = $('#direccion').val();
  const cuit = $('#cuit').val();

  // Realiza una solicitud AJAX para actualizar los datos del cliente
  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/clientes/${clientId}`,
    type: 'PUT',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    contentType: 'application/json',
    data: JSON.stringify({ nombre, email, direccion, cuit }),
    success: function (response) {
      // Cierra el modal después de la actualización exitosa
      $('#editarClienteModal').modal('hide');
      // Realiza cualquier otra acción necesaria después de la actualización
    },
    error: function (error) {
      console.error('Error al actualizar detalles del cliente:', error);

      // Imprime información adicional sobre el error
      console.log('Error status:', error.status);
      console.log('Error responseJSON:', error.responseJSON);
    }
  });
});



// Evento de clic para el botón "Eliminar"
$('#clientesTableBody').on('click', '.btn-delete', function () {
  const clientId = $(this).data('client-id');

  // Muestra un modal de confirmación
  $('#confirmarEliminarModal').modal('show');

  // Evento de clic para el botón "Confirmar"
  $('#confirmarEliminarBtn').on('click', function () {
    // Realiza una solicitud AJAX para eliminar el cliente
    $.ajax({
      url: `http://127.0.0.1:5500/usuarios/${userId}/clientes/${clientId}`,
      type: 'DELETE',
      headers: {
        'x-access-token': token,
        'user-id': userId
      },
      success: function (response) {
        // Cierra el modal después de la eliminación exitosa
        $('#confirmarEliminarModal').modal('hide');

        // Realiza cualquier otra acción necesaria después de la eliminación
      },
      error: function (error) {
        console.error('Error al eliminar cliente:', error);

        // Imprime información adicional sobre el error
        console.log('Error status:', error.status);
        console.log('Error responseJSON:', error.responseJSON);
      }
    });
  });
});

// Evento de clic para el botón "Cancelar" en el modal de confirmación
$('#cancelarEliminarBtn').on('click', function () {
  // Cierra el modal de confirmación
  $('#confirmarEliminarModal').modal('hide');
});



// Ejecuta la inicialización cuando el documento esté listo
$(document).ready(function () {
  inicializarTabla();
});


function cambiarPagina(page) {
  // Llama a la función para obtener y mostrar los datos de clientes paginados
  obtenerClientesPaginados(page);
}



// Evento de envío para el formulario de creación de cliente
$('#crearClienteForm').on('submit', function (event) {
  event.preventDefault();

  // Obtén los valores del formulario
  const nombreNuevo = $('#nombreNuevo').val();
  const emailNuevo = $('#emailNuevo').val();
  const direccionNuevo = $('#direccionNuevo').val();
  const cuitNuevo = $('#cuitNuevo').val();

  // Realiza una solicitud AJAX para crear un nuevo cliente
  $.ajax({
      url: `http://127.0.0.1:5500/usuarios/${userId}/clientes`,
      type: 'POST',
      headers: {
          'x-access-token': token,
          'user-id': userId
      },
      contentType: 'application/json',
      data: JSON.stringify({ nombre: nombreNuevo, email: emailNuevo, direccion: direccionNuevo, cuit: cuitNuevo }),
      success: function (response) {
          // Realiza cualquier acción necesaria después de la creación exitosa
          console.log('Cliente creado:', response);

          // Limpiar el formulario después de la creación exitosa
          $('#crearClienteForm')[0].reset();

          // Opcional: puedes agregar el nuevo cliente a la tabla si lo deseas
          // obtenerClientesPaginados(1);
      },
      error: function (error) {
          console.error('Error al crear cliente:', error);

          // Imprime información adicional sobre el error
          console.log('Error status:', error.status);
          console.log('Error responseJSON:', error.responseJSON);
      }
  });
});







// document.addEventListener('DOMContentLoaded', function () {
//   var links = document.querySelectorAll('a[data-target]');
//   var mainContent = document.querySelector('main');

//   links.forEach(function (link) {
//     link.addEventListener('click', function (event) {
//       event.preventDefault();
//       var targetFormId = link.getAttribute('data-target');
//       var targetForm = document.getElementById(targetFormId);

//       // Oculta todos los formularios y luego muestra el formulario deseado
//       mainContent.querySelectorAll('form').forEach(function (form) {
//         form.style.display = 'none';
//       });

//       targetForm.style.display = 'block';
//     });
//   });
// });

// //mostrar lista usuarios

// document.addEventListener("DOMContentLoaded", function () {
//   const clientesTableElement = document.getElementById("clientesTable");

//   if (clientesTableElement) {
//     const userId = obtenerUserIdDesdeLocalStorage();
//     const token = obtenerTokenDesdeLocalStorage();

//     if (!userId || !token) {
//       console.error("No se pudo obtener el ID de usuario o el token desde localStorage.");
//       return;
//     }

//     fetch(`http://127.0.0.1:5500/usuarios/${userId}/clientes`, {
//       method: 'GET',
//       headers: {
//         'x-access-token': token,
//         'user-id': userId
//       }
//     })
//       .then(response => response.json())
//       .then(data => {
//         if (data.length > 0) {
//           const table = document.createElement("table");
//           table.classList.add("table", "table-striped");

//           const thead = document.createElement("thead");
//           const headerRow = document.createElement("tr");

//           const idHeader = document.createElement("th");
//           idHeader.scope = "col";
//           idHeader.textContent = "ID";

//           const nombreHeader = document.createElement("th");
//           nombreHeader.scope = "col";
//           nombreHeader.textContent = "Nombre";

//           const emailHeader = document.createElement("th");
//           emailHeader.scope = "col";
//           emailHeader.textContent = "Email";

//           const direccionHeader = document.createElement("th");
//           direccionHeader.scope = "col";
//           direccionHeader.textContent = "Dirección";

//           headerRow.appendChild(idHeader);
//           headerRow.appendChild(nombreHeader);
//           headerRow.appendChild(emailHeader);
//           headerRow.appendChild(direccionHeader);
//           thead.appendChild(headerRow);
//           table.appendChild(thead);

//           const tbody = document.createElement("tbody");

//           data.forEach(cliente => {
//             const row = document.createElement("tr");

//             const idCell = document.createElement("td");
//             idCell.textContent = cliente.cliente_id;

//             const nombreCell = document.createElement("td");
//             nombreCell.textContent = cliente.nombre;

//             const emailCell = document.createElement("td");
//             emailCell.textContent = cliente.email;

//             const direccionCell = document.createElement("td");
//             direccionCell.textContent = cliente.direccion;

//             row.appendChild(idCell);
//             row.appendChild(nombreCell);
//             row.appendChild(emailCell);
//             row.appendChild(direccionCell);

//             tbody.appendChild(row);
//           });

//           table.appendChild(tbody);
//           clientesTableElement.appendChild(table);
//         } else {
//           clientesTableElement.textContent = "No hay clientes para mostrar.";
//         }
//       })
//       .catch(error => console.error("Error al obtener los clientes:", error));
//   } else {
//     console.error("No se encontró el elemento con id 'clientesTable' en el DOM.");
//   }

  
// });


// function obtenerUserIdDesdeLocalStorage() {
//   try {
//     const userData = JSON.parse(localStorage.getItem("user"));

//     if (userData && userData.user_data && userData.user_data.user_id) {
//       const userId = userData.user_data.user_id;
//       console.log("ID de usuario obtenido desde localStorage:", userId);
//       return userId;
//     } else {
//       console.error("La estructura no es válida en localStorage.user o no se encontró el user_id.");
//       return null;
//     }
//   } catch (error) {
//     console.error("Error al analizar JSON desde localStorage.user:", error);
//     return null;
//   }
// }


// document.addEventListener('DOMContentLoaded', function () {
//   // Obtener referencias a los elementos relevantes
//   var altaForm = document.getElementById('altaClienteForm');
//   var guardarClienteBtn = document.getElementById('guardar-cliente');

//   // Agregar evento de envío al formulario de Alta
//   altaForm.addEventListener('submit', function (event) {
//     event.preventDefault(); // Evita que el formulario se envíe y la página se recargue

//     // Obtiene los datos del formulario
//     var nombre_cliente = document.getElementById('Cliente').value;
//     var cuit = document.getElementById('cuit').value;
//     var email = document.getElementById('email').value;
//     var direccion = document.getElementById('direccion').value;

//     // Obtiene el token y el usuario desde el localStorage
//     var token = localStorage.getItem('token');
//     var userId = obtenerUserIdDesdeLocalStorage();

//     // Construye el objeto de datos a enviar al servidor
//     var data = {
//        nombre: nombre_cliente,
//        email: email,
//        direccion: direccion,
//        cuit: cuit,
//        id_usuario: userId
//     };

//     // Realiza la llamada a la ruta de creación de cliente
//     fetch(`http://127.0.0.1:5500/usuarios/${userId}/clientes`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//         'x-access-token': token,
//         'user-id': userId
//       },
//       body: JSON.stringify(data)
//     })
//       .then(response => response.json())
//       .then(responseData => {
//         // Muestra el mensaje de confirmación
//         var mensajeClienteGuardado = document.getElementById('mensajeClienteGuardado');
//         mensajeClienteGuardado.style.display = 'block';

//         // Oculta el mensaje después de unos segundos 
//         setTimeout(function () {
//           mensajeClienteGuardado.style.display = 'none';
//         }, 3000); // Oculta el mensaje después de 3 segundos 

//         // Limpia los campos del formulario
//         altaForm.reset();
//       })
//       .catch(error => {
//         console.error("Error al crear el cliente:", error);
//         // Puedes manejar el error de acuerdo a tus necesidades
//       });
//   });

//   // Agregar evento de clic al botón "Guardar"
//   guardarClienteBtn.addEventListener('click', function (event) {
    
//     altaForm.dispatchEvent(new Event('submit'));
//   });

//   // Agregar evento de clic a los enlaces
//   var links = document.querySelectorAll('a[data-target]');
//   var mainContent = document.querySelector('main');
//   var altaLink = document.querySelector('a[data-target="altaForm"]');

//   links.forEach(function (link) {
//     link.addEventListener('click', function (event) {
//       event.preventDefault();
//       var targetFormId = link.getAttribute('data-target');
//       var targetForm = document.getElementById(targetFormId);

//       // Oculta todos los formularios y luego muestra el formulario deseado
//       mainContent.querySelectorAll('form').forEach(function (form) {
//         form.style.display = 'none';
//       });

//       targetForm.style.display = 'block';

//       // Si es el formulario de Alta, también puedes realizar lógica adicional aquí
//       if (targetFormId === 'altaClienteForm') {
//         // Puedes agregar más lógica específica para el formulario de Alta aquí
//       }
//     });
//   });

//   // Agregar evento de clic al enlace de Alta
//   altaLink.addEventListener('click', function (event) {
//     event.preventDefault();
  
//     // Oculta todos los formularios existentes
//     mainContent.querySelectorAll('form').forEach(function (form) {
//       form.style.display = 'none';
//     });
  
//     // Muestra el formulario de alta
//     altaForm.style.display = 'block';
  
//     // Puedes agregar más lógica específica para el formulario de Alta aquí
//   });
//   });
// // });






// //MODIFICAR
// document.addEventListener('DOMContentLoaded', function () {
//   // Obtener referencia al formulario de Modificación
//   var modificarForm = document.getElementById('modificarClienteForm');
//   var modificarClienteBtn = document.getElementById('boton-modificar');
//   var clienteIdField = document.getElementById('IDMod');  // Campo para ingresar el ID del cliente

//   // Agregar evento de envío al formulario de Modificación
//   modificarForm.addEventListener('submit', function (event) {
//       event.preventDefault();
//       var clienteIdMod = clienteIdField.value;  // Obtiene el ID del cliente del campo de entrada

//       // Obtiene los datos del formulario
//       var nombreClienteMod = document.getElementById('nombreMod').value;
//       var cuitMod = document.getElementById('cuitMod').value;
//       var emailMod = document.getElementById('emailMod').value;
//       var direccionMod = document.getElementById('direccionMod').value;

//       // Obtiene el token y el usuario desde el localStorage
//       var token = localStorage.getItem('token');
//       var userId = obtenerUserIdDesdeLocalStorage();

//       // Construye el objeto de datos a enviar al servidor
//       var dataMod = {
//           nombre: nombreClienteMod,
//           email: emailMod,
//           direccion: direccionMod,
//           cuit: cuitMod,
//           id_usuario: userId
//       };

//       // Realiza la llamada a la ruta de modificación de cliente
//       fetch(`http://127.0.0.1:5500/usuarios/${userId}/clientes/${clienteIdMod}`, {
//           method: 'PUT',  // Utiliza el método PUT para actualizar el cliente
//           headers: {
//               'Content-Type': 'application/json',
//               'x-access-token': token,
//               'user-id': userId
//           },
//           body: JSON.stringify(dataMod)
//       })
//           .then(response => response.json())
//           .then(responseData => {
//               // Muestra el mensaje de confirmación
//               var mensajeClienteModificado = document.getElementById('mensajeClienteModificado');
//               mensajeClienteModificado.style.display = 'block';

//               // Oculta el mensaje después de unos segundos 
//               setTimeout(function () {
//                   mensajeClienteModificado.style.display = 'none';
//               }, 3000); // Oculta el mensaje después de 3 segundos 

//               // Limpia los campos del formulario
//               modificarForm.reset();
//           })
//           .catch(error => {
//               console.error("Error al modificar el cliente:", error);
//               // Puedes manejar el error de acuerdo a tus necesidades
//           });
//   });


//   // Agregar evento de clic al botón "Guardar"
//   modificarClienteBtn.addEventListener('click', function (event) {
    
//     modificarForm.dispatchEvent(new Event('submit'));
//   });

//   // Agregar evento de clic a los enlaces
//   var linksMod = document.querySelectorAll('a[data-target]');
//   var mainContent = document.querySelector('main');
//   var modificarLink = document.querySelector('a[data-target="modificarForm"]');

//   linksMod.forEach(function (link) {
//     link.addEventListener('click', function (event) {
//       event.preventDefault();
//       var targetFormId = link.getAttribute('data-target');
//       var targetForm = document.getElementById(targetFormId);

//       // Oculta todos los formularios y luego muestra el formulario deseado
//       mainContent.querySelectorAll('form').forEach(function (form) {
//         form.style.display = 'none';
//       });

//       targetForm.style.display = 'block';

//       // Si es el formulario de Alta, también puedes realizar lógica adicional aquí
//       if (targetFormId === 'modificarClienteForm') {
//         // Puedes agregar más lógica específica para el formulario de Alta aquí
//       }
//     });
//   });

//   // Agregar evento de clic al enlace de Alta
//   modificarLink.addEventListener('click', function (event) {
//     event.preventDefault();
//     modificarForm.style.display = 'block';

//     // Puedes agregar más lógica específica para el formulario de Alta aquí
//   });
// });


// //BAJA

// document.addEventListener('DOMContentLoaded', function () {
//   var bajaLink = document.querySelector('a[data-target="bajaForm"]');
//   var bajaForm = document.getElementById('bajaClienteForm');

//   bajaLink.addEventListener('click', function (event) {
//     event.preventDefault();
//     bajaForm.style.display = 'block';
//     // agregar más lógica aquí, como ocultar otros elementos, etc.
//   });
// });


// //facturas
// document.addEventListener('DOMContentLoaded', function () {
//   var facturasLink = document.querySelector('a[data-target="facturasForm"]');
//   var facturasForm = document.getElementById('facturasForm');

//   facturasLink.addEventListener('click', function (event) {
//       event.preventDefault();
//       facturasForm.style.display = 'block';

//       // Oculta otros formularios si es necesario
//       altaClienteForm.style.display = 'none';
//       modificarClienteForm.style.display = 'none';
//       bajaClienteForm.style.display = 'none';
//   });
// });


// // SALDO
// document.addEventListener('DOMContentLoaded', function () {
//   var saldoLink = document.querySelector('a[data-target="saldoForm"]');
//   var saldoForm = document.getElementById('saldoForm');

//   saldoLink.addEventListener('click', function (event) {
//       event.preventDefault();
//       saldoForm.style.display = 'block';

//       // Oculta otros formularios si es necesario
//       altaClienteForm.style.display = 'none';
//       modificarClienteForm.style.display = 'none';
//       bajaClienteForm.style.display = 'none';
//       facturasForm.style.display = 'none';
//   });
// });