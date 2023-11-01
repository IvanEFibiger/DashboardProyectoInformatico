CREATE DATABASE IF NOT EXISTS  db_pryecto_informatico;
USE db_proyecto_informatico;

CREATE TABLE IF NOT EXISTS usuario (
    id INT(10) NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);

INSERT INTO person VALUES
(1, 'Juan', 'Álvarez' , 12345678, 'juan@mail.com', 'pass'),
(2, 'Ana', 'Perez' , 87654321, 'ana@mail.com', 'pass');


CREATE TABLE IF NOT EXISTS clientes (
    id INT(10) NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    id_usuario INT(10),
    FOREIGN KEY (id_usuario) REFERENCES usuario (id)
);

INSERT INTO client VALUES
(1, 'Dai', 'dai@gmail.com', 'calle 1 120', 1),
(2, 'maria', 'maria@gmail.com', 'calle 2 240', 1),
(3, 'marta', 'marta@gmail.com', 'calle 3 360', 2),
(4, 'jose', 'jose@gmail.com', 'calle 4 480', 2);
(3, 'marta', 'marta@gmail.com', 'calle 3 360', 2),
(4, 'jose', 'jose@gmail.com', 'calle 4 480', 2);

CREATE TABLE IF NOT EXISTS factura (
    id INT(10) NOT NULL AUTO_INCREMENT,
    fecha_emision DATE NOT NULL,
    id_clientes INT(10),
    id_usuario INT(10),
    PRIMARY KEY (id),
    FOREIGN KEY (id_clientes) REFERENCES clientes (id),
    FOREIGN KEY (id_usuario) REFERENCES usuario (id)
);


CREATE TABLE IF NOT EXISTS Detalle_factura (
    id INT(10) NOT NULL AUTO_INCREMENT,
    id_factura INT(10),
    id_producto INT(10),
    id_servicio INT(10),
    cantidad INT(10),
    precio_unitario DECIMAL(10, 2),
    subtotal DECIMAL(10, 2),
    PRIMARY KEY (id),
    FOREIGN KEY (id_factura) REFERENCES facturas (id),
    FOREIGN KEY (id_producto) REFERENCES Producto (id),
    FOREIGN KEY (id_servicio) REFERENCES Servicio (id)
);

CREATE TABLE IF NOT EXISTS Servicio (
    id INT(10) NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS Producto (
    id INT(10) NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS Movimiento_stock (
    id INT(10) NOT NULL AUTO_INCREMENT,
    producto_id INT(10) NOT NULL,
    tipo VARCHAR(255) NOT NULL,
    cantidad INT(10) NOT NULL,
    fecha DATE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (producto_id) REFERENCES Producto (id)
);







