document.addEventListener("DOMContentLoaded", function() {
  var loginLink = document.getElementById("loginLink");
  var loginPopup = document.getElementById("loginPopup");
  var closePopup = document.getElementById("closePopup");
  var loginForm = document.getElementById("loginForm");
  var loginButton = document.getElementById("loginButton");
  var logoutLink = document.getElementById('logoutLink');
  if (logoutLink) {
      logoutLink.addEventListener('click', function (event) {
          event.preventDefault();
  
          // Get the token from localStorage
          const token = localStorage.getItem('token');
  
          // Check if a valid token is available before calling logoutUser
          if (token) {
              // Call logoutUser function with the token
              logoutUser(token);
          } else {
              alert("No se encontró un token válido en localStorage.");
          }
      });
  } else {
      console.error('El enlace de logout no se encontró en el DOM.');
  }


  // Abre el popup al hacer clic en el enlace
  loginLink.addEventListener("click", function(e) {
      e.preventDefault();
      loginPopup.style.display = "block";
  });

  // Cierra el popup al hacer clic en el botón de cierre
  closePopup.addEventListener("click", function() {
      loginPopup.style.display = "none";
  });

  // Cierra el popup al hacer clic fuera del contenido
  window.addEventListener("click", function(event) {
      if (event.target === loginPopup) {
          loginPopup.style.display = "none";
      }
  });

  // Evita que el formulario se envíe y procesa el inicio de sesión
  loginForm.addEventListener("submit", function(e) {
      e.preventDefault();

      var username = document.getElementById("in-username").value;
      var password = document.getElementById("password").value;

      // Realiza una solicitud POST a tu endpoint de inicio de sesión
      fetch("http://localhost:5500/login", {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
              "authorization": "Basic " + btoa(username + ":" + password)
          },
          body: JSON.stringify({
              username: username,
              password: password,
          }),
      })
      .then(response => response.json())
      .then(data => {
          if (data.token) {
              // Almacena el token en localStorage
              localStorage.setItem("token", data.token);

              // Realiza una solicitud GET para obtener la información del usuario
              return fetch("http://localhost:5500/usuarios/" + data.id, {
                  method: "GET",
                  headers: {
                      "Content-Type": "application/json",
                      "x-access-token": data.token,
                      "user-id": data.id
                  },
              });
          } else {
              // Muestra un mensaje de error en caso de inicio de sesión fallido
              alert("Inicio de sesión fallido: " + data.message);
          }
      })
      .then(response => response.json())
      .then(user => {
          // Almacena la información del usuario en localStorage
          localStorage.setItem("user", JSON.stringify(user));
          console.log("User data:", user);

          // Cierra el popup después del inicio de sesión exitoso
          loginPopup.style.display = "none";

          // Redirige a la página dashboard.html
          window.location.href = "dashboard.html";
      })
      .catch(error => console.error("Error:", error));
  });

  // Función para cerrar sesión
  f// Función para cerrar sesión
  function logoutUser(token) {
    if (!token) {
        alert("No se proporcionó un token válido.");
        return;
    }

    // Realiza una solicitud al servidor para cerrar la sesión
    fetch('http://localhost:5500/logout', {
        method: 'POST',
        headers: {
            'Authorization': 'Basic ' + token
        }
    })
    .then(response => {
        if (response.ok) {
            // Elimina el token y la información del usuario del almacenamiento local
            localStorage.removeItem('token');
            localStorage.removeItem('user');

            // Redirige al usuario a la página de inicio
            window.location.href = 'index.html';
        } else {
            // Si la respuesta no es 'OK', muestra un mensaje de error
            return response.json().then(data => Promise.reject(data));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Aquí puedes agregar código adicional para manejar el error según tus necesidades
        alert("Error al cerrar sesión: " + error.message);
    });

}

// Evento para el enlace de deslogueo
var logoutLink = document.getElementById('logoutLink');
if (logoutLink) {
    logoutLink.addEventListener('click', function(event) {
        event.preventDefault();

        // Realiza las acciones necesarias para cerrar la sesión
        logoutUser();
    });
} else {
    console.error('El enlace de logout no se encontró en el DOM.');
}

});

