// Llama a esta función para obtener y mostrar los datos de servicios paginados
function obtenerServiciosPaginados(page) {
  const url = `http://127.0.0.1:5500/usuarios/${userId}/servicios-paginados?page=${page}`;

  $.ajax({
    url: url,
    type: 'GET',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    success: function (data) {
      // Limpia el cuerpo de la tabla
      $('#serviciosTableBody').empty();

      // Itera sobre los datos y agrega filas a la tabla
      data.service.forEach(function (servicio) {
        const row = `<tr>
                       <td>${servicio.servicio_id}</td>
                       <td>${servicio.nombre}</td>
                       <td>${servicio.descripcion}</td>
                       <td>${servicio.precio}</td>
                       <td>
                       <button class="btn btn-secondary btn-edit" data-service-id="${servicio.servicio_id}">Editar</button>
                       <button class="btn btn-danger btn-delete" data-service-id="${servicio.servicio_id}">Eliminar</button>
                       </td>
                     </tr>`;
        $('#serviciosTableBody').append(row);
      });

      // Actualiza la paginación
      actualizarPaginacion(data.total_pages, data.current_page);
    },
    error: function (error) {
      console.error('Error al obtener servicios paginados:', error);
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

// Llama a esta función para inicializar la tabla con la primera página de servicios
function inicializarTabla() {
  obtenerServiciosPaginados(1);
}

$('.pagination').on('click', 'a.page-link', function (event) {
  event.preventDefault(); // Evita que el enlace recargue la página

  // Obtén el número de página desde el atributo data-page
  const page = $(this).data('page');

  // Llama a la función cambiarPagina con el número de página
  cambiarPagina(page);
});



// Evento de clic para el botón "Editar"
$('#serviciosTableBody').on('click', '.btn-edit', function () {
  const serviceId = $(this).data('service-id');

  // Realiza una solicitud AJAX para obtener los detalles del servicio
  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/servicios/${serviceId}`, // Corregido clientId a serviceId
    type: 'GET',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    success: function (servicio) {
      // Muestra un pop-up con el formulario de edición
      mostrarFormularioEdicion(servicio);
    },
    error: function (error) {
      console.error('Error al obtener detalles del servicio:', error);
    }
  });
});

// Función para mostrar el pop-up con el formulario de edición
function mostrarFormularioEdicion(servicio) {
  // Llena los campos del formulario con los datos del servicio
  $('#nombre').val(servicio.nombre);
  $('#descripcion').val(servicio.descripcion);
  $('#precio').val(servicio.precio); 

  // Almacena el ID del servicio en un atributo de datos del botón "Guardar Cambios"
  $('#guardarCambiosServicio').data('service-id', servicio.servicio_id);

  // Muestra el modal
  $('#editarServiciosModal').modal('show');
}

// Evento de clic para el botón "Guardar Cambios"
$('#guardarCambiosServicio').on('click', function () {
  // Obtén el ID del servicio almacenado en el atributo de datos del botón
  const serviceId = $(this).data('service-id');

  // Obtén los valores actualizados del formulario
  const nombre = $('#nombre').val();
  const descripcion = $('#descripcion').val();
  const precio = $('#precio').val(); // Corregido email a precio

  // Realiza una solicitud AJAX para actualizar los datos del servicio
  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/servicios/${serviceId}`,
    type: 'PUT',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    contentType: 'application/json',
    data: JSON.stringify({ nombre, descripcion, precio  }),
    success: function (response) {
      // Cierra el modal después de la actualización exitosa
      $('#editarServiciosModal').modal('hide');
      // Realiza cualquier otra acción necesaria después de la actualización
    },
    error: function (error) {
      console.error('Error al actualizar detalles del servicio:', error);

      // Imprime información adicional sobre el error
      console.log('Error status:', error.status);
      console.log('Error responseJSON:', error.responseJSON);
    }
  });
});


// Evento de clic para el botón "Eliminar"
$('#serviciosTableBody').on('click', '.btn-delete', function () {
  const serviceId = $(this).data('service-id'); // 

  // Muestra un modal de confirmación
  $('#confirmarEliminarModal').modal('show');

  // Evento de clic para el botón "Confirmar"
  $('#confirmarEliminarBtn').off().on('click', function () {
    // Realiza una solicitud AJAX para eliminar el servicio
    $.ajax({
      url: `http://127.0.0.1:5500/usuarios/${userId}/servicios/${serviceId}`, 
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
        console.error('Error al eliminar servicio:', error);

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
  // Llama a la función para obtener y mostrar los datos de servicios paginados
  obtenerServiciosPaginados(page);
}



// Evento de envío para el formulario de creación de servicio
$('#crearServicioForm').on('submit', function (event) {
  event.preventDefault();

  // Obtén los valores del formulario
  const nombreNuevo = $('#nombreNuevo').val();
  const descripcionNuevo = $('#descripcionNuevo').val(); // Corregido a #descripcionNuevo
  const precioNuevo = $('#precioNuevo').val();

  // Realiza una solicitud AJAX para crear un nuevo servicio
  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/servicios`,
    type: 'POST',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    contentType: 'application/json',
    data: JSON.stringify({
      nombre: nombreNuevo,
      descripcion: descripcionNuevo,
      precio: precioNuevo
    }),
    success: function (response) {
      // Realiza cualquier acción necesaria después de la creación exitosa
      console.log('Servicio creado:', response);

      // Limpiar el formulario después de la creación exitosa
      $('#crearServicioForm')[0].reset();

      // Muestra el mensaje de confirmación
      $('#mensajeServicioGuardado').show();

      // Puedes ocultar el mensaje después de un tiempo específico si lo deseas
      setTimeout(function () {
        $('#mensajeServicioGuardado').hide();
      }, 3000); // Oculta el mensaje después de 3 segundos
    },
    error: function (error) {
      console.error('Error al crear servicio:', error);

      // Imprime información adicional sobre el error
      console.log('Error status:', error.status);
      console.log('Error responseJSON:', error.responseJSON);
    }
  });
});




