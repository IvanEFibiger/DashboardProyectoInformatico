// Función para mostrar el detalle de la factura
function mostrarDetalleFactura(facturaId) {
  const url = `http://127.0.0.1:5500/usuarios/${userId}/factura/${facturaId}`;

  $.ajax({
    url: url,
    type: 'GET',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    success: function (data) {
      llenarModalFactura(data);
      $('#facturaModal').modal('show');
    },
    error: function (error) {
      console.error('Error al obtener detalle de factura:', error);
    }
  });
}

// Llama a esta función para obtener y mostrar los datos de facturas paginadas
function obtenerFacturasPaginadas(page) {
  const url = `http://127.0.0.1:5500/usuarios/${userId}/facturas/detalles?page=${page}`;

  $.ajax({
    url: url,
    type: 'GET',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    success: function (data) {
      // Limpia el cuerpo de la tabla
      $('#facturasTableBody').empty();  // Utiliza el ID correcto

      // Itera sobre los datos y agrega filas a la tabla
      data.facturas_detalles.forEach(function (factura) {
        const row = `<tr>
                       <td>${factura.factura_id}</td>
                       <td>${factura.fecha_emision}</td>
                       <td>${factura.nombre_cliente}</td>
                       <td>${factura.total}</td>
                       <td>
                         <button class="btn btn-secondary btn-ver" data-factura-id="${factura.factura_id}">Ver</button>
                         <button class="btn btn-secondary btn-exportar-pdf" id="exportar" data-factura-id="${factura.factura_id}">Exportar a PDF</button>
                         <button class="btn btn-danger btn-delete" data-factura-id="${factura.factura_id}">Eliminar</button>
                       </td>
                     </tr>`;
        $('#facturasTableBody').append(row);  // Utiliza el ID correcto
      });

      // Actualiza la paginación
      actualizarPaginacion(data.total_pages, data.current_page);

      // Manejador de clics en los botones "Ver"
      $('.btn-ver').on('click', function () {
        const facturaId = $(this).data('factura-id');
        mostrarDetalleFactura(facturaId);
      });
    },
    error: function (error) {
      console.error('Error al obtener facturas paginadas:', error);
    }
  });
}

// Función para actualizar la paginación
function actualizarPaginacion(totalPages, currentPage) {
  // Elimina los elementos actuales de la paginación
  $('.pagination').empty();

  // Agrega el botón "Anterior"
  const prevButton = $('<li class="page-item"></li>');
  const prevLink = $(`<a class="page-link" href="#" data-page="${currentPage - 1}">Anterior</a>`);
  prevButton.append(prevLink);
  $('.pagination').append(prevButton);

  // Agrega botones para cada página
  for (let i = 1; i <= totalPages; i++) {
    const pageButton = $('<li class="page-item"></li>');
    const pageLink = $(`<a class="page-link" href="#" data-page="${i}">${i}</a>`);
    // Marca la página actual como activa
    if (i === currentPage) {
      pageButton.addClass('active');
    }
    pageButton.append(pageLink);
    $('.pagination').append(pageButton);
  }

  // Agrega el botón "Siguiente"
  const nextButton = $('<li class="page-item"></li>');
  const nextLink = $(`<a class="page-link" href="#" data-page="${currentPage + 1}">Siguiente</a>`);
  nextButton.append(nextLink);
  $('.pagination').append(nextButton);

  // Deshabilita el botón "Anterior" si estamos en la primera página
  if (currentPage === 1) {
    prevButton.addClass('disabled');
  }

  // Deshabilita el botón "Siguiente" si estamos en la última página
  if (currentPage === totalPages) {
    nextButton.addClass('disabled');
  }
}

// Llama a esta función para inicializar la tabla con la primera página de facturas
function inicializarTabla() {
  obtenerFacturasPaginadas(1);
}

// Función para mostrar el detalle de la factura
function mostrarDetalleFactura(facturaId) {
  const url = `http://127.0.0.1:5500/usuarios/${userId}/factura/${facturaId}`;

  $.ajax({
    url: url,
    type: 'GET',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    success: function (data) {
      llenarModalFactura(data);
      $('#facturaModal').modal('show');
    },
    error: function (error) {
      console.error('Error al obtener detalle de factura:', error);
    }
  });
}

function formatearFecha(fecha) {
  const options = { day: 'numeric', month: 'numeric', year: 'numeric' };
  const fechaFormateada = new Date(fecha).toLocaleDateString(undefined, options);
  return fechaFormateada;
}
let contenidoModal = '';
// Función para llenar dinámicamente los campos del modal con datos de la factura
function llenarModalFactura(data) {
  const factura = data.factura;
  const detalles = data.detalles;
  const cliente = data.cliente;
  const nombreUsuario = obtenerNombreDeUsuarioDesdeLocalStorage();
  const fechaFormateada = formatearFecha(factura.fecha_emision);
  const productos_servicios = data.productos_servicios;
  // Construir el contenido HTML del modal
  const contenidoFactura = `
    <div class="row mb-3">
      <div class="col-md-6 text-right">
        <h6 id="tituloFactura">FACTURA</h6>
        <div class="col-md-6">
        <h6 id="nombreUsuario">${nombreUsuario}</h6>
        </div>
        <div class="row mb-3">
          <div class="col-md-6">
            <h6 id="nombreCliente">Nombre del Cliente: <span class="font-weight-bold">${cliente.nombre_cliente}</span></h6>
            <p id="cuitCliente" class="mb-0">CUIT del Cliente: <span class="font-weight-bold">${cliente.cuit_cliente}</span></p>
          </div>
          <div class="col-md-6 text-right">
            <p id="numeroFactura" class="mb-0">Número de Factura: <span class="font-weight-bold">${factura.factura_id}</span></p>
            <p id="fechaFactura" class="mb-0">Fecha de Emisión: <span class="font-weight-bold">${fechaFormateada}</span></p>
          </div>
        </div>

    <div class="row mb-3">
      <div class="col-md-12">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Producto o Servicio</th>
              <th>Cantidad</th>
              <th>Precio Unitario</th>
              <th>Subtotal</th>
            </tr>
          </thead>
          <tbody>
            ${detalles.map(detalle => `
              <tr>
                <td>${detalle.id_producto ? detalle.id_producto : detalle.id_servicio}</td>
                <td>${detalle.id_producto ? productos_servicios.find(ps => ps.producto_id === detalle.id_producto)?.nombre : productos_servicios.find(ps => ps.servicio_id === detalle.id_servicio)?.nombre}</td>
                <td>${detalle.cantidad}</td>
                <td>${detalle.precio_unitario}</td>
                <td>${detalle.subtotal}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>

    <div class="border-top mt-3 pt-3" id="divTotal">
      <p class="mb-0" >Importe Total: ${factura.total}</p>
    </div>
  `;

  // Insertar el contenido en el modal
  $('#facturaModal .modal-body').html(contenidoFactura);

  // Mostrar el modal
  $('#facturaModal').modal('show');
  contenidoModal = contenidoFactura;

}



// Manejador de clics en los enlaces de paginación
$('.pagination').on('click', 'a.page-link', function (event) {
  event.preventDefault(); // Evita que el enlace recargue la página

  // Obtén el número de página desde el atributo data-page
  const page = $(this).data('page');

  // Llama a la función para obtener y mostrar los datos de facturas paginadas
  obtenerFacturasPaginadas(page);
});

// Ejecuta la inicialización cuando el documento esté listo
$(document).ready(function () {
  inicializarTabla();
});
$(document).ready(function () {
$('#facturasTableBody').on('click', '.btn-exportar-pdf', function () {
  // Obtén el ID de la factura desde el atributo data-factura-id
  const facturaId = $(this).data('factura-id');

  // Muestra el detalle de la factura
  mostrarDetalleFactura(facturaId);

  // Imprime el modal como PDF
  imprimirModalComoPDF();
});
});


$('#facturaModal').on('click', '#imprimirFactura', function () {
  imprimirModal();
});

// Función para imprimir el contenido del modal
function imprimirModal() {
  // Obtén el elemento del modal
  const element = document.getElementById('facturaModal');

  if (element) {
    // Abre el cuadro de diálogo de impresión del navegador
    window.print();
  } else {
    console.error('No se pudo encontrar el elemento del modal para imprimir.');
  }
}
// Evento de clic para el botón "Eliminar" de facturas
$('#facturasTableBody').on('click', '.btn-delete', function () {
  const facturaId = $(this).data('factura-id');

  // Muestra un modal de confirmación
  $('#confirmarEliminarFacturaModal').modal('show');

  // Evento de clic para el botón "Confirmar" en el modal de confirmación de facturas
  $('#confirmarEliminarFacturaBtn').on('click', function () {
    // Realiza una solicitud AJAX para eliminar la factura
    $.ajax({
      url: `http://127.0.0.1:5500/usuarios/${userId}/factura/${facturaId}`,
      type: 'DELETE',
      headers: {
        'x-access-token': token,
        'user-id': userId
      },
      success: function (response) {
        // Cierra el modal después de la eliminación exitosa
        $('#confirmarEliminarFacturaModal').modal('hide');

        // Realiza cualquier otra acción necesaria después de la eliminación

        // Actualiza la tabla de facturas después de eliminar
        obtenerFacturasPaginadas(1);
      },
      error: function (error) {
        console.error('Error al eliminar factura:', error);

        // Imprime información adicional sobre el error
        console.log('Error status:', error.status);
        console.log('Error responseJSON:', error.responseJSON);
      }
    });
  });
});

// Evento de clic para cancelar la eliminación en el modal de confirmación de facturas
$('#confirmarEliminarFacturaModal').on('hidden.bs.modal', function () {
  // Remueve el manejador de clic para el botón "Confirmar" cuando se cierra el modal
  $('#confirmarEliminarFacturaBtn').off('click');
});

// Evento de clic para cancelar la eliminación en el modal de confirmación de facturas
$('#confirmarEliminarFacturaModal').on('hidden.bs.modal', function () {
  // Remueve el manejador de clic para el botón "Confirmar" cuando se cierra el modal
  $('#confirmarEliminarFacturaBtn').off('click');
});



//Crear factura
let selectedClientId;
let addingProduct = false;
let addingService = false;


// Función para cargar clientes
function cargarClientes() {
  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/clientes`, 
    type: 'GET',
    headers: {
      'x-access-token': token,
      'user-id': userId // Reemplaza con el ID del usuario actual
    },
    success: function (data) {
      const clienteDropdown = $('#cliente');
      clienteDropdown.empty(); // Limpia opciones existentes
      clienteDropdown.append('<option value="">Seleccione cliente</option>');

      // Agrega opciones al dropdown
      data.forEach(function (cliente) {
        clienteDropdown.append(`<option value="${cliente.cliente_id}">${cliente.nombre}</option>`);
        console.log(`<option value="${cliente.cliente_id}">${cliente.nombre}</option>`);
      });

      // Manejador de cambio del elemento select
      clienteDropdown.on('change', function () {
        // Guarda el ID del cliente seleccionado y conviértelo a un número
        selectedClientId = $(this).val();
      });
    },
    error: function (error) {
      console.error('Error al cargar clientes:', error);
    }
  });
}

function cargarProductos() {
  const selectProductos = $('.producto:last');

  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/productos`,
    type: 'GET',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    success: function (data) {
      selectProductos.empty();
      selectProductos.append('<option value="">Seleccionar producto</option>');

      data.forEach(function (producto) {
        // Filtrar productos del usuario autenticado
        if (producto.id_usuario === userId) {
          selectProductos.append(`<option value="${producto.producto_id}">${producto.nombre}</option>`);
          console.log("estoy en el foreach de cargar producto" +`<option value="${producto.producto_id}">${producto.nombre}</option>`);
        }
      });
    },
    error: function (error) {
      console.error('Error al cargar productos:', error);
    }
  });
}

function cargarServicios() {
  const selectServicios = $('.servicio:last');

  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/servicios`,
    type: 'GET',
    headers: {
      'x-access-token': token,
      'user-id': userId
    },
    success: function (data) {
      selectServicios.empty();
      selectServicios.append('<option value="">Seleccionar servicio</option>');

      data.forEach(function (servicio) {
        // Filtrar servicios del usuario autenticado
        if (servicio.id_usuario === userId) {
          selectServicios.append(`<option value="${servicio.servicio_id}">${servicio.nombre}</option>`);
          console.log("estoy en el foreach de cargar servicio" +`<option value="${servicio.servicio_id}">${servicio.nombre}</option>`);
        }
      });
    },
    error: function (error) {
      console.error('Error al cargar servicios:', error);
    }
  });
}

// Función para agregar dinámicamente campos de productos y servicios
function agregarProductoServicio() {
  const container = $('#productosServicios');
  const nuevoCampo = `
    <div>
      <label>Cantidad:</label>
      <input type="number" min="1" required>

      <label>Producto:</label>
      <select class="producto" ${addingProduct ? '' : 'disabled'} required>
        <!-- Opciones se llenarán dinámicamente con JavaScript -->
      </select>

      <label>Servicio:</label>
      <select class="servicio" ${addingService ? '' : 'disabled'} required>
        <!-- Opciones se llenarán dinámicamente con JavaScript -->
      </select>
    </div>
  `;

  container.append(nuevoCampo);

  // Cargar dinámicamente productos y servicios en el nuevo campo
  cargarProductos();
  cargarServicios();
}


// Manejador de clic para el botón "Agregar Producto"
function agregarProducto() {
  addingProduct = true;
  addingService = false;
  agregarProductoServicio();
}

// Manejador de clic para el botón "Agregar Servicio"
function agregarServicio() {
  addingProduct = false;
  addingService = true;
  agregarProductoServicio();
}


// Función para crear la factura

let selectedProductIds = [];
let selectedServiceIds = [];

// Manejador de cambio para clientes
$(document).on('change', '#cliente', function () {
  // Guarda la ID del cliente seleccionado en el objeto
  selectedIds.cliente = $(this).val();
});

// Manejador de cambio para productos
$(document).on('change', '.producto', function () {
  // Limpia el array de IDs de productos antes de agregar nuevas selecciones
  selectedProductIds = [];

  // Itera sobre los elementos .producto y agrega las IDs seleccionadas al array
  $('.producto').each(function () {
    const productId = $(this).val();
    if (productId) {
      selectedProductIds.push(parseInt(productId));
    }
  });
});

// Manejador de cambio para servicios
$(document).on('change', '.servicio', function () {
  // Limpia el array de IDs de servicios antes de agregar nuevas selecciones
  selectedServiceIds = [];

  // Itera sobre los elementos .servicio y agrega las IDs seleccionadas al array
  $('.servicio').each(function () {
    const serviceId = $(this).val();
    if (serviceId) {
      selectedServiceIds.push(parseInt(serviceId));
    }
  });
});

// Función para crear la factura
function crearFactura() {
  const fechaEmision = $('#fecha_emision').val();
  const clienteSeleccionado = $('#cliente').val();

  // Validación de la fecha y cliente seleccionado
  if (!fechaEmision || !clienteSeleccionado) {
    alert('Por favor, complete los campos solicitados.');
    return;
  }
  // Obtiene los valores del formulario
  const formData = {
    fecha_emision: $('#fecha_emision').val(),
    id_clientes: selectedClientId,
    id_usuario: userId,
    productos_servicios: []
  };

  // Itera sobre los campos de productos y servicios agregados dinámicamente
  $('#productosServicios > div').each(function () {
    const cantidad = $(this).find('input[type=number]').val();

    // Utiliza las variables de IDs de productos y servicios
    const id_producto = $(this).find('.producto').val();
    const id_servicio = $(this).find('.servicio').val();

    // Agrega el objeto al array de productos_servicios solo si hay al menos uno de los IDs
    if (id_producto !== '' || id_servicio !== '') {
      formData.productos_servicios.push({
        cantidad: parseInt(cantidad),
        id_producto: id_producto !== '' ? parseInt(id_producto) : null,
        id_servicio: id_servicio !== '' ? parseInt(id_servicio) : null
      });
    }
  });

  // Realiza la solicitud POST al servidor
  $.ajax({
    url: `http://127.0.0.1:5500/usuarios/${userId}/factura`,
    type: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-access-token': token,
      'user-id': userId
    },
    data: JSON.stringify(formData),
    success: function (data) {
      console.log('Factura creada exitosamente:', data);
      location.reload();
    },
    error: function (error) {
      console.error('Error al crear factura:', error);
    }
  });
}


// Cargar clientes al inicio
cargarClientes();