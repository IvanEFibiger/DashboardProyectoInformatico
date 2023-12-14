  // mostrar/ocultar el "Dashboard"
$(document).ready(function () {
  // Agrega un evento de clic a la pestaña "Dashboard"
  $('.nav-link[href="#mobileMenu"]').on('click', function () {
      // Alterna el estado del menú desplegable
      $('#mobileMenu').offcanvas('toggle');
  });
});


//obtener nombres de usuario y token para mostrar
function obtenerTokenDesdeLocalStorage() {
  const token = localStorage.getItem("token");
  console.log("Token obtenido desde localStorage:", token);
  return token;
}

function obtenerUserIdDesdeLocalStorage() {
  try {
    const userData = JSON.parse(localStorage.getItem("user"));

    if (userData && userData.user_data && userData.user_data.user_id) {
      const userId = userData.user_data.user_id;
      console.log("ID de usuario obtenido desde localStorage:", userId);
      return userId;
    } else {
      console.error("La estructura no es válida en localStorage.user o no se encontró el user_id.");
      return null;
    }
  } catch (error) {
    console.error("Error al analizar JSON desde localStorage.user:", error);
    return null;
  }
}

// Ejemplo de uso:


function obtenerNombreDeUsuarioDesdeLocalStorage() {
  try {
    const userData = JSON.parse(localStorage.getItem("user"));

    if (userData && userData.user_data && userData.user_data.user) {
      const nombreUsuario = userData.user_data.user;
      console.log("Nombre de usuario obtenido desde localStorage:", nombreUsuario);
      return nombreUsuario;
    } else {
      console.error("La estructura no es válida en localStorage.user.");
      return null;
    }
  } catch (error) {
    console.error("Error al analizar JSON desde localStorage.user:", error);
    return null;
  }
}


// Ejemplo de uso:
// Obtener nombre de usuario cuando sea necesario

// Ejemplo de uso:
// Obtener token y nombre de usuario cuando sea necesario
const token = obtenerTokenDesdeLocalStorage();
const nombreUsuario = obtenerNombreDeUsuarioDesdeLocalStorage();
const userId = obtenerUserIdDesdeLocalStorage();
console.log(userId);
console.log(token)
console.log(nombreUsuario)


function mostrarNombreDeUsuarioEnUI() {
  const nombreUsuario = obtenerNombreDeUsuarioDesdeLocalStorage();

  if (nombreUsuario) {
      const usernamePlaceholder = document.getElementById("usernamePlaceholder");

      if (usernamePlaceholder) {
          // Actualiza el contenido del elemento usernamePlaceholder con el nombre del usuario
          usernamePlaceholder.textContent = nombreUsuario;
      } else {
          console.error("No se encontró el elemento con id 'usernamePlaceholder' en el DOM.");
      }
  } else {
      console.error("No se pudo obtener el nombre de usuario desde localStorage.");
  }
}



//para ingresos
document.addEventListener("DOMContentLoaded", function() {
  // Obtener el elemento HTML donde se mostrarán los ingresos
  const ingresosTotalesElement = document.getElementById("ingresos-totales");

  if (ingresosTotalesElement) {
      // Obtener el ID de usuario y el token desde localStorage
      const userId = obtenerUserIdDesdeLocalStorage();
      const token = obtenerTokenDesdeLocalStorage();

      if (!userId || !token) {
          console.error("No se pudo obtener el ID de usuario o el token desde localStorage.");
          return;
      }

      // Hacer una solicitud AJAX al endpoint Flask para obtener los ingresos
      fetch(`http://127.0.0.1:5500/usuarios/${userId}/factura/total`, {
          method: 'GET',
          headers: {
              'x-access-token': token,
              'user-id': userId
          }
      })
      .then(response => response.json())
      .then(data => {
          // Obtener el valor de ingresos desde la respuesta de la ruta Flask
          const totalFacturasUsuario = data.total_facturas_usuario;

          // Formatear el valor como número con dos decimales
          const ingresos = parseFloat(totalFacturasUsuario).toFixed(2);

          // Actualizar el contenido del elemento HTML con el valor de ingresos
          ingresosTotalesElement.textContent = `Ingresos: $${ingresos}`;
      })
      .catch(error => console.error("Error al obtener los ingresos:", error));
  } else {
      console.error("No se encontró el elemento con id 'ingresos-totales' en el DOM.");
  }

  // Mostrar el nombre de usuario en la interfaz de usuario
  mostrarNombreDeUsuarioEnUI();
});

//cantidad facturas

document.addEventListener("DOMContentLoaded", function() {
  // Obtener el elemento HTML donde se mostrará la cantidad de facturas
  const cantidadFacturasElement = document.getElementById("facturas-emitidas");

  if (cantidadFacturasElement) {
      // Obtener el ID de usuario y el token desde localStorage
      const userId = obtenerUserIdDesdeLocalStorage();
      const token = obtenerTokenDesdeLocalStorage();

      if (!userId || !token) {
          console.error("No se pudo obtener el ID de usuario o el token desde localStorage.");
          return;
      }

      // Hacer una solicitud AJAX al nuevo endpoint Flask para obtener la cantidad de facturas
      fetch(`http://127.0.0.1:5500/usuarios/${userId}/factura/cantidad`, {
          method: 'GET',
          headers: {
              'x-access-token': token,
              'user-id': userId
          }
      })
      .then(response => response.json())
      .then(data => {
          // Obtener la cantidad de facturas desde la respuesta de la ruta Flask
          const cantidadFacturas = data.cantidad_facturas_usuario;

          // Actualizar el contenido del elemento HTML con el valor de ingresos
          cantidadFacturasElement.textContent = `Total de facturas emitidas: ${cantidadFacturas}`;
      })
      .catch(error => console.error("Error al obtener la cantidad de facturas:", error));
  } else {
      console.error("No se encontró el elemento con id 'cantidad-facturas' en el DOM.");
  }

  // Mostrar el nombre de usuario en la interfaz de usuario
  mostrarNombreDeUsuarioEnUI();
});


//producto mas vendido

document.addEventListener("DOMContentLoaded", function() {
  // Obtener el elemento HTML donde se mostrará la cantidad de facturas
  const prodMasVendidoElement = document.getElementById("producto-principal");

  if (prodMasVendidoElement) {
      // Obtener el ID de usuario y el token desde localStorage
      const userId = obtenerUserIdDesdeLocalStorage();
      const token = obtenerTokenDesdeLocalStorage();

      if (!userId || !token) {
          console.error("No se pudo obtener el ID de usuario o el token desde localStorage.");
          return;
      }

      // Hacer una solicitud AJAX al nuevo endpoint Flask para obtener la cantidad de facturas
      fetch(`http://127.0.0.1:5500/usuarios/${userId}/factura/producto-mas-vendido`, {
          method: 'GET',
          headers: {
              'x-access-token': token,
              'user-id': userId
          }
      })
      .then(response => response.json())
      .then(data => {
          // Obtener la cantidad de facturas desde la respuesta de la ruta Flask
          const nombreProducto = data.producto_mas_vendido;

          // Actualizar el contenido del elemento HTML con el valor de ingresos
          prodMasVendidoElement.textContent = `Producto más vendido: ${nombreProducto}`;
      })
      .catch(error => console.error("Error al obtener la cantidad de facturas:", error));
  } else {
      console.error("No se encontró el elemento con id 'cantidad-facturas' en el DOM.");
  }

  // Mostrar el nombre de usuario en la interfaz de usuario
  mostrarNombreDeUsuarioEnUI();
});


//cantidad clientes

document.addEventListener("DOMContentLoaded", function() {
  // Obtener el elemento HTML donde se mostrará la cantidad de facturas
  const cantidadClientesElement = document.getElementById("clientes-cantidad");

  if (cantidadClientesElement) {
      // Obtener el ID de usuario y el token desde localStorage
      const userId = obtenerUserIdDesdeLocalStorage();
      const token = obtenerTokenDesdeLocalStorage();

      if (!userId || !token) {
          console.error("No se pudo obtener el ID de usuario o el token desde localStorage.");
          return;
      }

      // Hacer una solicitud AJAX al nuevo endpoint Flask para obtener la cantidad de facturas
      fetch(`http://127.0.0.1:5500//usuarios/${userId}/cantidad-clientes`, {
          method: 'GET',
          headers: {
              'x-access-token': token,
              'user-id': userId
          }
      })
      .then(response => response.json())
      .then(data => {
          // Obtener la cantidad de facturas desde la respuesta de la ruta Flask
          const cantidad = data.cantidad_clientes;

          // Actualizar el contenido del elemento HTML con el valor de ingresos
          cantidadClientesElement.textContent = `Cantidad de clientes: ${cantidad}`;
      })
      .catch(error => console.error("Error al obtener la cantidad de facturas:", error));
  } else {
      console.error("No se encontró el elemento con id 'cantidad-facturas' en el DOM.");
  }

  // Mostrar el nombre de usuario en la interfaz de usuario
  mostrarNombreDeUsuarioEnUI();
});


//ranking productos

document.addEventListener("DOMContentLoaded", function () {
  const prodMasVendidosElement = document.getElementById("producto-ranking");

  if (prodMasVendidosElement) {
    const userId = obtenerUserIdDesdeLocalStorage();
    const token = obtenerTokenDesdeLocalStorage();

    if (!userId || !token) {
      console.error("No se pudo obtener el ID de usuario o el token desde localStorage.");
      return;
    }

    fetch(`http://127.0.0.1:5500/usuarios/${userId}/ranking-productos`, {
      method: 'GET',
      headers: {
        'x-access-token': token,
        'user-id': userId
      }
    })
      .then(response => response.json())
      .then(data => {
        const productosMasVendidos = data;

        if (productosMasVendidos.length > 0) {
          const table = document.createElement("table");
          table.classList.add("table");

          const thead = document.createElement("thead");
          const headerRow = document.createElement("tr");

          const nombreHeader = document.createElement("th");
          nombreHeader.scope = "col";
          nombreHeader.textContent = "Producto";

          const cantidadHeader = document.createElement("th");
          cantidadHeader.scope = "col";
          cantidadHeader.textContent = "Cantidad Vendida";

          headerRow.appendChild(nombreHeader);
          headerRow.appendChild(cantidadHeader);
          thead.appendChild(headerRow);
          table.appendChild(thead);

          const tbody = document.createElement("tbody");

          // Mostrar solo los primeros 5 productos más vendidos
          for (let i = 0; i < Math.min(5, productosMasVendidos.length); i++) {
            const producto = productosMasVendidos[i];

            const row = document.createElement("tr");

            const nombreCell = document.createElement("td");
            nombreCell.textContent = producto.nombre_producto;

            const cantidadCell = document.createElement("td");
            cantidadCell.textContent = producto.cantidad_vendida;

            row.appendChild(nombreCell);
            row.appendChild(cantidadCell);

            tbody.appendChild(row);
          }

          table.appendChild(tbody);

          prodMasVendidosElement.appendChild(table);
        } else {
          prodMasVendidosElement.textContent = "No hay productos vendidos.";
        }
      })
      .catch(error => console.error("Error al obtener los productos más vendidos:", error));
  } else {
    console.error("No se encontró el elemento con id 'producto-principal' en el DOM.");
  }

  mostrarNombreDeUsuarioEnUI();
});



//ranking servicios

document.addEventListener("DOMContentLoaded", function () {
  const servMasVendidosElement = document.getElementById("servicio-ranking");

  if (servMasVendidosElement) {
    const userId = obtenerUserIdDesdeLocalStorage();
    const token = obtenerTokenDesdeLocalStorage();

    if (!userId || !token) {
      console.error("No se pudo obtener el ID de usuario o el token desde localStorage.");
      return;
    }

    fetch(`http://127.0.0.1:5500/usuarios/${userId}/ranking-servicios`, {
      method: 'GET',
      headers: {
        'x-access-token': token,
        'user-id': userId
      }
    })
      .then(response => response.json())
      .then(data => {
        const servMasVendidos = data;

        if (servMasVendidos.length > 0) {
          const table = document.createElement("table");
          table.classList.add("table");

          const thead = document.createElement("thead");
          const headerRow = document.createElement("tr");

          const nombreHeader = document.createElement("th");
          nombreHeader.scope = "col";
          nombreHeader.textContent = "Servicio";

          const cantidadHeader = document.createElement("th");
          cantidadHeader.scope = "col";
          cantidadHeader.textContent = "Cantidad Vendida";

          headerRow.appendChild(nombreHeader);
          headerRow.appendChild(cantidadHeader);
          thead.appendChild(headerRow);
          table.appendChild(thead);

          const tbody = document.createElement("tbody");

          // Mostrar solo los primeros 5 productos más vendidos
          for (let i = 0; i < Math.min(5, servMasVendidos.length); i++) {
            const servicio = servMasVendidos[i];

            const row = document.createElement("tr");

            const nombreCell = document.createElement("td");
            nombreCell.textContent = servicio.nombre_servicio;

            const cantidadCell = document.createElement("td");
            cantidadCell.textContent = servicio.cantidad_vendida;

            row.appendChild(nombreCell);
            row.appendChild(cantidadCell);

            tbody.appendChild(row);
          }

          table.appendChild(tbody);

          servMasVendidosElement.appendChild(table);
        } else {
          servMasVendidosElement.textContent = "No hay servicios vendidos.";
        }
      })
      .catch(error => console.error("Error al obtener los servicios más vendidos:", error));
  } else {
    console.error("No se encontró el elemento con id 'servicio-principal' en el DOM.");
  }

  mostrarNombreDeUsuarioEnUI();
});


//Ranking clientes


document.addEventListener("DOMContentLoaded", function () {
  const clienteDestacadoElement = document.getElementById("cliente-ranking");

  if (clienteDestacadoElement) {
    const userId = obtenerUserIdDesdeLocalStorage();
    const token = obtenerTokenDesdeLocalStorage();

    if (!userId || !token) {
      console.error("No se pudo obtener el ID de usuario o el token desde localStorage.");
      return;
    }

    fetch(`http://127.0.0.1:5500/usuarios/${userId}/ranking-clientes`, {
      method: 'GET',
      headers: {
        'x-access-token': token,
        'user-id': userId
      }
    })
      .then(response => response.json())
      .then(data => {
        const clienteDestacado = data;

        if (clienteDestacado.length > 0) {
          const table = document.createElement("table");
          table.classList.add("table");

          const thead = document.createElement("thead");
          const headerRow = document.createElement("tr");

          const nombreHeader = document.createElement("th");
          nombreHeader.scope = "col";
          nombreHeader.textContent = "Cliente";

          const cantidadHeader = document.createElement("th");
          cantidadHeader.scope = "col";
          cantidadHeader.textContent = "Total gastado";

          headerRow.appendChild(nombreHeader);
          headerRow.appendChild(cantidadHeader);
          thead.appendChild(headerRow);
          table.appendChild(thead);

          const tbody = document.createElement("tbody");

          // Mostrar solo los primeros 5 productos más vendidos
          for (let i = 0; i < Math.min(5, clienteDestacado.length); i++) {
            const cliente = clienteDestacado[i];

            const row = document.createElement("tr");

            const nombreCell = document.createElement("td");
            nombreCell.textContent = cliente.nombre_cliente;

            const cantidadCell = document.createElement("td");
            cantidadCell.textContent = cliente.total_gastado;

            row.appendChild(nombreCell);
            row.appendChild(cantidadCell);

            tbody.appendChild(row);
          }

          table.appendChild(tbody);

          clienteDestacadoElement.appendChild(table);
        } else {
          clienteDestacadoElement.textContent = "No hay clientes para mostrar.";
        }
      })
      .catch(error => console.error("Error al obtener los clientes destacados:", error));
  } else {
    console.error("No se encontró el elemento con id 'servicio-principal' en el DOM.");
  }

  mostrarNombreDeUsuarioEnUI();
});



//STOCK


document.addEventListener("DOMContentLoaded", function () {
  const contenidoControlStockElement = document.getElementById("contenidoControlStock");

  if (contenidoControlStockElement) {
    const userId = obtenerUserIdDesdeLocalStorage();
    const token = obtenerTokenDesdeLocalStorage();

    if (!userId || !token) {
      console.error("No se pudo obtener el ID de usuario o el token desde localStorage.");
      return;
    }

    function actualizarContenido(id_user, token) {
      fetch(`http://127.0.0.1:5500/usuarios/${id_user}/stock_movimientos`, {
        method: 'GET',
        headers: {
          'x-access-token': token,
          'user-id': id_user
        }
      })
        .then(response => response.json())
        .then(data => {
          // Agrupar productos por colores
          const productosPorColores = {};
          data.forEach(producto => {
            const colorFondo = producto.stock_real > 5 ? 'green' : (producto.stock_real >= 1 && producto.stock_real <= 4 ? 'yellow' : 'red');
            productosPorColores[colorFondo] = productosPorColores[colorFondo] || [];
            productosPorColores[colorFondo].push(producto);
          });
    
          // Construir la tabla con el contenido actualizado
          var tablaContenido = '<table class="table">';
          tablaContenido += '<thead><tr><th>Producto</th><th>Stock actual</th></tr></thead>';
          tablaContenido += '<tbody>';
    
          Object.keys(productosPorColores).forEach(color => {
            //tablaContenido += `<tr><th colspan="2" style="background-color: ${color};">${color}</th></tr>`;
            productosPorColores[color].forEach(producto => {
              tablaContenido += `<tr><td  style="background-color: ${color};">${producto.producto}</td><td style="background-color: ${color};">${producto.stock_real}</td></tr>`;
            });
          });
    
          tablaContenido += '</tbody></table>';
    
          // Actualizar el contenido de la tarjeta de control de stock
          contenidoControlStockElement.innerHTML = tablaContenido;
        })
        .catch(error => console.error("Error al obtener los movimientos de stock:", error));
    }

    // Llamada inicial al cargar la página
    actualizarContenido(userId, token);

    // Llamada repetitiva cada 5 segundos
    setInterval(function () {
      actualizarContenido(userId, token);
    }, 5000);
  } else {
    console.error("No se encontró el elemento con id 'contenidoControlStock' en el DOM.");
  }

  mostrarNombreDeUsuarioEnUI();
});



//historial ventas

document.addEventListener("DOMContentLoaded", function () {
  const historialVentasList = document.getElementById("historialVentasList");

  if (historialVentasList) {
    const userId = obtenerUserIdDesdeLocalStorage();
    const token = obtenerTokenDesdeLocalStorage();

    if (!userId || !token) {
      console.error("No se pudo obtener el ID de usuario o el token desde localStorage.");
      return;
    }

    function mostrarUltimasVentas(id_user, token) {
      fetch(`http://127.0.0.1:5500/usuarios/${id_user}/historial_ventas`, {
        method: 'GET',
        headers: {
          'x-access-token': token,
          'user-id': id_user
        }
      })
        .then(response => response.json())
        .then(data => {
          // Limpiar el contenido actual
          historialVentasList.innerHTML = '';

          // Construir la tabla con las últimas 10 ventas
          const table = document.createElement("table");
          table.classList.add("table");

          const thead = document.createElement("thead");
          const headerRow = document.createElement("tr");

          const productoHeader = document.createElement("th");
          productoHeader.textContent = "Producto";

          const cantidadHeader = document.createElement("th");
          cantidadHeader.textContent = "Cantidad";

          const fechaHeader = document.createElement("th");
          fechaHeader.textContent = "Fecha de Venta";

          headerRow.appendChild(productoHeader);
          headerRow.appendChild(cantidadHeader);
          headerRow.appendChild(fechaHeader);

          thead.appendChild(headerRow);
          table.appendChild(thead);

          const tbody = document.createElement("tbody");

          for (let i = 0; i < Math.min(5, data.length); i++) {
            const venta = data[i];
            const row = document.createElement("tr");

            const productoCell = document.createElement("td");
            productoCell.textContent = venta.producto;

            const cantidadCell = document.createElement("td");
            cantidadCell.textContent = venta.cantidad;

            const fechaCell = document.createElement("td");
            fechaCell.textContent = venta.fecha_emision;

            row.appendChild(productoCell);
            row.appendChild(cantidadCell);
            row.appendChild(fechaCell);

            tbody.appendChild(row);
          }

          table.appendChild(tbody);

          // Agregar la tabla al contenedor
          historialVentasList.appendChild(table);
        })
        .catch(error => console.error("Error al obtener el historial de ventas:", error));
    }

    // Llamar a la función inicialmente al cargar la página
    mostrarUltimasVentas(userId, token);

  } else {
    console.error("No se encontró el elemento con id 'historialVentasList' en el DOM.");
  }
});