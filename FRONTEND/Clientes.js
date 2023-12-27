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
          alert('Cliente creado:', response);
          // Limpiar el formulario después de la creación exitosa
          $('#crearClienteForm')[0].reset();
          location.reload();
      },
      error: function (error) {
          console.error('Error al crear cliente:', error);

          // Imprime información adicional sobre el error
          console.log('Error status:', error.status);
          console.log('Error responseJSON:', error.responseJSON);
      }
  });
});





