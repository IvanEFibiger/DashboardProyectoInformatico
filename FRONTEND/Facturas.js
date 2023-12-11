$(document).ready(function () {
    // Agrega un evento a los botones "Ver Factura"
    $('.verFacturaBtn').click(function () {
      // Obtén el ID de la factura desde el atributo data
      var idFactura = $(this).data('id');
  
      // Llama a la función para cargar el contenido de la factura
      cargarContenidoFactura(idFactura);
    });
  });
  
  // Función para cargar el contenido de la factura
  
    function cargarContenidoFactura(idFactura) {
        // Aquí deberías cargar dinámicamente los detalles de la factura
        // según el ID de la factura proporcionado
      
        // Ejemplo de datos de factura (deberías obtener estos datos de tu aplicación)
        var factura = {
          id: idFactura,
          fechaEmision: 'Fecha de Emisión',
          cliente: 'Cliente de Ejemplo',
          valor: '$1000',
          // Otros campos de la factura
          idProducto: '1',
          nombreProducto: 'Nombre del Producto o Servicio',
          cantidad: '5',
          precioUnitario: '$200',
          subtotal: '$1000',
          total: '$1200',
        };
      
        // Llenar dinámicamente los campos del modal con datos de la factura
        var contenidoFactura = `
          <div class="row mb-3">
            <div class="col-md-6">
              <h6>Nombre del Usuario</h6>
            </div>
            <div class="col-md-6 text-right">
              <h6>FACTURA</h6>
              <p class="mb-0">Número de Factura: <span class="font-weight-bold">00000 00000000</span></p>
              <p class="mb-0">Fecha de Emisión: <span class="font-weight-bold">${factura.fechaEmision}</span></p>
            </div>
          </div>
      
          <div class="row mb-3">
            <div class="col-md-6">
              <p class="mb-0">CUIT del Cliente: <span class="font-weight-bold">12345678901</span></p>
              <p class="mb-0">Nombre del Cliente: <span class="font-weight-bold">${factura.cliente}</span></p>
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
                  <tr>
                    <td>${factura.idProducto}</td>
                    <td>${factura.nombreProducto}</td>
                    <td>${factura.cantidad}</td>
                    <td>${factura.precioUnitario}</td>
                    <td>${factura.subtotal}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
      
          <div class="border-top mt-3 pt-3">
            <p class="mb-1">Subtotal: ${factura.subtotal}</p>
            <p class="mb-0">Importe Total: ${factura.total}</p>
          </div>
        `;
      
        // Insertar el contenido en el modal
        $('#facturaModal .modal-body').html(contenidoFactura);
      
        // Mostrar el modal
        $('#facturaModal').modal('show');
      }
    






      //agregar factura
      $(document).ready(function () {
        // Contadores para identificar los elementos
        var contadorProductos = 1;
      
        // Evento para agregar un nuevo producto al formulario
        $('#agregarProducto').click(function () {
          contadorProductos++;
      
          // Clona el último conjunto de campos y modifica los IDs y nombres
          var nuevoProducto = $('#detallesProductos .mb-3:first').clone();
          nuevoProducto.find('.form-label').each(function () {
            var nuevoID = $(this).attr('for') + contadorProductos;
            $(this).attr('for', nuevoID);
          });
          nuevoProducto.find('.form-control').each(function () {
            var nuevoID = $(this).attr('id') + contadorProductos;
            $(this).attr('id', nuevoID).attr('name', $(this).attr('name').replace(/\d+/, contadorProductos)).val('');
          });
      
          // Inserta el nuevo conjunto de campos en el formulario
          $('#detallesProductos').append(nuevoProducto);
        });
      
        // Evento para mostrar el modal de confirmación antes de generar la factura
        $('#generarFactura').click(function (e) {
          e.preventDefault(); // Evita que el formulario se envíe automáticamente
      
          // Lógica para construir el contenido de la factura en el modal
          var contenidoFactura = `
            <div class="row mb-3">
              <div class="col-md-6">
                <h6>Nombre del Usuario</h6>
              </div>
              <div class="col-md-6 text-right">
                <h6>FACTURA</h6>
                <p class="mb-0">Número de Factura: <span class="font-weight-bold">00000 00000000</span></p>
                <p class="mb-0">Fecha de Emisión: <span class="font-weight-bold">${$('#fechaEmision').val()}</span></p>
              </div>
            </div>
      
            <div class="row mb-3">
              <div class="col-md-6">
                <p class="mb-0">Cliente: <span class="font-weight-bold">${$('#cliente').val()}</span></p>
              </div>
            </div>
      
            <div class="row mb-3">
              <div class="col-md-12">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Producto/Servicio</th>
                      <th>Cantidad</th>
                      <th>Precio Unitario</th>
                      <th>Subtotal</th>
                    </tr>
                  </thead>
                  <tbody>`;
      
          // Detalles de los productos o servicios
          $('#detallesProductos .mb-3').each(function () {
            var producto = $(this).find('.producto').val();
            var cantidad = $(this).find('.cantidad').val();
            var precio = $(this).find('.precio').val();
        
            // Verificar si el usuario ha ingresado valores antes de agregar la fila
            if (producto && cantidad && precio) {
              var subtotal = cantidad * precio;
        
              contenidoFactura += `
                <tr>
                  <td>${producto}</td>
                  <td>${cantidad}</td>
                  <td>${precio}</td>
                  <td>${subtotal}</td>
                </tr>`;
            }
          });
      
          // Cierre de la tabla y otras secciones
          contenidoFactura += `
                </tbody>
              </table>
            </div>
          </div>
      
          <div class="border-top mt-3 pt-3">
            <p class="mb-1">Subtotal: $${calcularSubtotal()}</p>
            <p class="mb-0">Importe Total: $${calcularTotal()}</p>
          </div>
        `;
      
          // Inserta el contenido en el modal
          $('#confirmacionModal .modal-body').html(contenidoFactura);
      
          // Muestra el modal
          $('#confirmacionModal').modal('show');
        });
      
        // Función para calcular el subtotal de la factura
        function calcularSubtotal() {
          var subtotal = 0;
          $('#detallesProductos .mb-3').each(function () {
            var cantidad = $(this).find('.cantidad').val();
            var precio = $(this).find('.precio').val();
            if (cantidad && precio) {
              subtotal += cantidad * precio;
            }
          });
          return subtotal;
        }
      
        // Función para calcular el total de la factura
        function calcularTotal() {
          return calcularSubtotal(); // Puedes agregar lógica adicional aquí según tus necesidades
        }
      });
      