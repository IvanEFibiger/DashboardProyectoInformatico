# 🧭 Dashboard Proyecto Informático

Proyecto final desarrollado para la **Tecnicatura Universitaria en Tecnologías de la Programación**
**Universidad Provincial del Sudoeste (UPSO)**
Materia: *Proyecto Informático*
Profesor: **Carlos Berger**
Grupo 7 — **Iván Fibiger**, **Daiana Saavedra**

---

## 🚀 Descripción General

**Dashboard Proyecto Informático** es una aplicación web fullstack diseñada para la gestión integral de clientes, productos, servicios, facturación y control de stock.
El sistema implementa autenticación JWT, control de acceso por usuario, políticas de seguridad revisadas y comunicación API REST entre backend y frontend.

* **Backend:** Flask (Python) con MySQL
* **Frontend:** React + TypeScript + Vite
* **Autenticación:** JWT (Bearer) + Refresh Token (con cookies HttpOnly)
* **Persistencia:** MySQL (Flask-MySQLdb)
* **Límite de peticiones:** Flask-Limiter
* **CORS y seguridad:** Flask-CORS + validaciones en endpoints

---

## 🧩 Estructura del Proyecto

```
DashboardProyectoInformatico/
├── BACKEND/
│   ├── api/
│   │   ├── db/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── __init__.py
│   │   ├── Utilidades.py
│   │   └── ...
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
└── frontend/
    ├── src/
    │   ├── api/
    │   ├── components/
    │   ├── pages/
    │   ├── security/
    │   ├── services/
    │   └── main.tsx
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts
```

---

## ⚙️ Requisitos Previos

* **Python 3.11+**
* **Node.js 20+**
* **MySQL 8.0+**
* **Git** (opcional)

---

## 🐍 Configuración del Backend (Flask)

### 1️⃣ Crear entorno virtual

```bash
cd BACKEND
python -m venv venv
```

### 2️⃣ Activar entorno virtual

**Windows PowerShell**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar variables de entorno

Crear un archivo `.env` en `BACKEND/` con el siguiente contenido:

```env
# Flask / JWT
FLASK_ENV=development
SECRET_KEY=<TU_SECRET_KEY>

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=<TU_USUARIO_DB>
MYSQL_PASSWORD=<TU_PASSWORD_DB>
MYSQL_DB=db_proyecto_informatico
MYSQL_CURSORCLASS=DictCursor
MYSQL_CHARSET=utf8mb4

ENV=development
BOOTSTRAP_ADMIN_TOKEN=<TOKEN_ADMIN_INICIAL>

# JWT Config
JWT_ISS=https://api.idsmart.local
JWT_AUD=https://app.idsmart.local
ACCESS_TTL_MIN=30
REFRESH_TTL_DAYS=15
FRONTEND_ORIGIN=http://localhost:5173

```

### 5️⃣ Ejecutar el servidor

```bash
python main.py
```

Servidor disponible en:

> [http://127.0.0.1:5500/](http://127.0.0.1:5500/)

---

## ⚛️ Configuración del Frontend (React + TypeScript)

### 1️⃣ Instalar dependencias

```bash
cd frontend
npm install
```

### 2️⃣ Configurar variables de entorno

Crear `.env.local` en la carpeta `frontend/`:

```env
VITE_API_BASE_URL=http://127.0.0.1:5500
```

### 3️⃣ Ejecutar entorno de desarrollo

```bash
npm run dev
```

Servidor disponible en:

> [http://localhost:5173/](http://localhost:5173/)

---

## 🔒 Autenticación y Seguridad

* **Login** → `/login` devuelve access y refresh tokens.
* **Refresh** → `/auth/refresh` renueva el token JWT de acceso.
* **Front** almacena sólo el access token; el refresh se maneja con cookie HttpOnly.
* Axios intercepta respuestas `401` y solicita renovación automática.

---

## 📊 Funcionalidades Principales

* Gestión de **Usuarios** (registro, login, logout).
* CRUD completo de **Clientes**, **Productos** y **Servicios**.
* Emisión y consulta de **Facturas**.
* Seguimiento de **Movimientos de Stock**.
* Reportes y estadísticas de ventas.
* Paginación, validaciones y mensajes de error claros en UI.
* Seguridad reforzada (rate limit, CORS estricto, tokens verificados en headers).

---

## 🧠 Tecnologías Utilizadas

**Backend**

* Flask 3.1
* Flask-MySQLdb
* Flask-Limiter
* Flask-CORS
* PyJWT
* python-dotenv

**Frontend**

* React 18
* TypeScript
* Vite 7
* Axios
* TailwindCSS (UI limpia y responsive)

---

## 🧱 Arquitectura General

```
Frontend (React/TS)
   ↓ Axios (Bearer Token)
Backend (Flask REST API)
   ↓
Base de Datos MySQL
```

---

## 👥 Autores

* **Iván Ever Fibiger** — Desarrollo Backend, Arquitectura, Seguridad, Integración API
* **Daiana Saavedra** — Diseño UI/UX, Interfaz Frontend, Testing

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos dentro de la **Universidad Provincial del Sudoeste (UPSO)**.
Puede ser reutilizado con fines educativos o de demostración.
