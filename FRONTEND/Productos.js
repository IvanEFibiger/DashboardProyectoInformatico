
// Llama a esta función para obtener y mostrar los datos de clientes paginados
function obtenerProductosPaginados(page) {
  const url = `http://127.0.0.1:5500/usuarios/${userId}/productos-paginados?page=${page}`;

  $.ajax({
    url: url,
    type: 'GET',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    success: function (data) {
      // Limpia el cuerpo de la tabla
      $('#productosTableBody').empty();

      // Itera sobre los datos y agrega filas a la tabla
      data.Products.forEach(function (producto) {
        const row = `<tr>
                       <td>${producto.producto_id}</td>
                       <td>${producto.nombre}</td>
                       <td>${producto.descripcion}</td>
                       <td>${producto.precio}</td>
                       <td>
                       <button class="btn btn-secondary btn-edit" data-product-id="${producto.producto_id}">Editar</button>
                       <button class="btn btn-success btn-stock" data-product-id="${producto.producto_id}">Stock</button>
                       <button class="btn btn-success btn-agregar" data-product-id="${producto.producto_id}">Agregar</button>
                       <button class="btn btn-danger btn-delete" data-product-id="${producto.producto_id}">Eliminar</button>
                       </td>
                     </tr>`;
        $('#productosTableBody').append(row);
      });

      // Actualiza la paginación
      actualizarPaginacion(data.total_pages, data.current_page);
    },
    error: function (error) {
      console.error('Error al obtener productos paginados:', error);
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
  obtenerProductosPaginados(1);
}

$('.pagination').on('click', 'a.page-link', function (event) {
  event.preventDefault(); // Evita que el enlace recargue la página

  // Obtén el número de página desde el atributo data-page
  const page = $(this).data('page');

  // Llama a la función cambiarPagina con el número de página
  cambiarPagina(page);
});

// Evento de clic para el botón "Editar" de productos
$('#productosTableBody').on('click', '.btn-edit', function () {
  const productId = $(this).data('product-id');

  // Realiza una solicitud AJAX para obtener los detalles del producto
  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/productos/${productId}`,
    type: 'GET',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    success: function (producto) {
      // Muestra un pop-up con el formulario de edición
      mostrarFormularioEdicionProducto(producto);
    },
    error: function (error) {
      console.error('Error al obtener detalles del producto:', error);
    }
  });
});

// Función para mostrar el pop-up con el formulario de edición de productos
function mostrarFormularioEdicionProducto(producto) {
  // Llena los campos del formulario con los datos del producto
  $('#nombre').val(producto.nombre);
  $('#descripcion').val(producto.descripcion);
  $('#precio').val(producto.precio);


  
  // Establece el valor de cantidad y deshabilita el campo
  $('#cantidad').val(producto.cantidad).prop('disabled', true);
  // Almacena el ID del producto en un atributo de datos del botón "Guardar Cambios"
  $('#guardarCambiosProducto').data('product-id', producto.producto_id);

  // Muestra el modal
  $('#editarProductoModal').modal('show');
}

// Evento de clic para el botón "Guardar Cambios" de productos
$('#guardarCambiosProducto').on('click', function () {
  // Obtén el ID del producto almacenado en el atributo de datos del botón
  const productId = $(this).data('product-id');

  // Obtén los valores actualizados del formulario
  const nombre = $('#nombre').val();
  const descripcion = $('#descripcion').val();
  const precio = $('#precio').val();
  const cantidad = $('#cantidad').val();

  
  // Realiza una solicitud AJAX para actualizar los datos del producto
  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/productos/${productId}`,
    type: 'PUT',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    contentType: 'application/json',
    data: JSON.stringify({ nombre, descripcion, precio, cantidad }),
    success: function (response) {
      // Cierra el modal después de la actualización exitosa
      $('#editarProductoModal').modal('hide');
      // Realiza cualquier otra acción necesaria después de la actualización
    },
    error: function (error) {
      console.error('Error al actualizar detalles del producto:', error);

      // Imprime información adicional sobre el error
      console.log('Error status:', error.status);
      console.log('Error responseJSON:', error.responseJSON);
    }
  });
});


// Evento de clic para el botón "Eliminar"
$('#productosTableBody').on('click', '.btn-delete', function () {
  const productId = $(this).data('product-id');

  // Muestra un modal de confirmación
  $('#confirmarEliminarModal').modal('show');

  // Evento de clic para el botón "Confirmar"
  $('#confirmarEliminarBtn').on('click', function () {
    // Realiza una solicitud AJAX para eliminar el cliente
    $.ajax({
      url: `http://127.0.0.1:5500/usuarios/${userId}/productos/${productId}`,
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


$('#productosTableBody').on('click', '.btn-stock', function () {
  const productId = $(this).data('product-id');

  // Realiza una solicitud AJAX para obtener el último stock del producto
  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/productos/${productId}/ultimo_stock`,
    type: 'GET',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    success: function (stockInfo) {
      // Muestra un pop-up con la información de stock
      mostrarInfoStock(stockInfo);
    },
    error: function (error) {
      console.error('Error al obtener información de stock:', error);
    }
  });
});

// Función para mostrar el modal de información de stock
function mostrarInfoStock(stockInfo) {
  // Construye el contenido del modal con la información de stock
  let modalContent = `<p>Stock actual: ${stockInfo.stock_real}</p>`;

  // Actualiza el cuerpo del modal con el contenido construido
  $('#infoStockModal .modal-body').html(modalContent);

  // Muestra el modal de información de stock
  $('#infoStockModal').modal('show');

  // Asigna el ID del producto al botón de cargar stock
  $('#btnCargarStock').data('product-id', stockInfo.producto_id);
}


// Función para mostrar el modal de información de stock
function mostrarInfoStock(stockInfo) {
  // Construye el contenido del modal con la información de stock
  let modalContent = `<p>Stock actual: ${stockInfo.stock_real}</p>`;






  // Actualiza el cuerpo del modal con el contenido construido
  $('#infoStockModal .modal-body').html(modalContent);

  // Muestra el modal de información de stock
  $('#infoStockModal').modal('show');
}

//cantidad de stock

// Evento de clic para el botón "Agregar"
$('#productosTableBody').on('click', '.btn-agregar', function () {
  const productId = $(this).data('product-id');

  // Asigna el ID del producto al formulario de carga de stock
  $('#cargarStockForm').data('product-id', productId);

  // Abre el modal de información de stock
  $('#cargarStockModal').modal('show');
});

// Evento de envío del formulario de carga de stock
$('#cargarStockForm').submit(function (event) {
  event.preventDefault();

  // Obtiene el ID del producto y la cantidad ingresada
  const productId = $(this).data('product-id');
  const nuevaCantidad = parseInt($('#cantidadInput').val(), 10);



  // Realiza una solicitud AJAX para actualizar la cantidad de stock
  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/productos/${productId}/stock`,
    type: 'PUT',
    contentType: 'application/json',
    data: JSON.stringify({ cantidad: nuevaCantidad }),
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    success: function (response) {
      console.log(response);


      // Cierra el modal de carga de stock
      $('#cargarStockModal').modal('hide');
    },
    error: function (error) {
      console.error('Error al cargar stock:', error);
    }
  });
});






// Ejecuta la inicialización cuando el documento esté listo
$(document).ready(function () {
  inicializarTabla();
});


function cambiarPagina(page) {
  // Llama a la función para obtener y mostrar los datos de clientes paginados
  obtenerProductosPaginados(page);
}








// Evento de envío para el formulario de creación de cliente
$('#crearProductoForm').on('submit', function (event) {
  event.preventDefault();

  // Obtén los valores del formulario
  const nombreNuevo = $('#nombreNuevo').val();
  const descripcionNuevo = $('#descripcionNuevo').val();
  const precioNuevo = $('#precioNuevo').val();
  const cantidadNuevo = $('#cantidadNuevo').val();



  console.log("Datos a enviar al servidor:", {
    nombre: nombreNuevo,
    descripcion: descripcionNuevo,
    precio: precioNuevo,
    cantidad: cantidadNuevo,
    id_usuario: userId
  });



  // Realiza una solicitud AJAX para crear un nuevo producto
  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/productos`,
    type: 'POST',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    contentType: 'application/json',
    data: JSON.stringify({ nombre: nombreNuevo, descripcion: descripcionNuevo, precio: precioNuevo, cantidad: cantidadNuevo, id_usuario: userId}),  
    success: function (response) {
      // Realiza cualquier acción necesaria después de la creación exitosa
      console.log('Producto creado:', response);

      alert("Producto guardado")
      $('#crearProductoForm')[0].reset();
      location.reload();
    },
    error: function (error) {
      console.error('Error al crear producto:', error);

      // Imprime información adicional sobre el error
      console.log('Error status:', error.status);
      console.log('Error responseJSON:', error.responseJSON);
    }
  });
});
