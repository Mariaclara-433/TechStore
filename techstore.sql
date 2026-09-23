-- ==========================================
-- CREAR BASE DE DATOS TECHSTORE
-- ==========================================

DROP DATABASE IF EXISTS techstore;

CREATE DATABASE techstore
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

USE techstore;


-- ==========================================
-- TABLA: USUARIOS
-- ==========================================

CREATE TABLE usuarios (
    id INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(80) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('Administrador', 'Cliente') DEFAULT 'Cliente',
    estado ENUM('Activo', 'Inactivo') DEFAULT 'Activo',
    telefono VARCHAR(20) NOT NULL,

    PRIMARY KEY (id),
    UNIQUE KEY correo (correo)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_0900_ai_ci;


-- ==========================================
-- DATOS DE USUARIOS
-- ==========================================

-- para obtener  de la contraseña del admin se debe hacer estos pasos:
-- 1. abrir la terminal de vscode del proyecto
-- 2. asegurarse de tener el .venv activado
-- 3. ejecutar el siguiente comando: python
-- 4. ejecutar el siguiente código en la terminal de python:
--    from werkzeug.security import generate_password_hash
-- 5. ejecutar el siguiente código en la terminal de python:
--    generate_password_hash('admin123')
-- 6. copiar el hash generado con todo y scrypt y reemplazarlo en el campo password donde dice 'PEGA_AQUI_EL_HASH'
INSERT INTO usuarios
(nombre, correo, telefono, password, rol, estado)
VALUES
(
    'Administrador TechStore',
    'admin@techstore.com',
    '3000000000',
    'PEGA_AQUI_EL_HASH',
    'Administrador',
    'Activo'
);


-- ==========================================
-- TABLA: PRODUCTOS
-- ==========================================

CREATE TABLE productos (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    imagen VARCHAR(255) DEFAULT NULL,

    PRIMARY KEY (codigo)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_0900_ai_ci;


-- ==========================================
-- DATOS DE PRODUCTOS
-- ==========================================

INSERT INTO productos
(codigo, nombre, precio, categoria, imagen)
VALUES
('P001', 'fiona', 780.00, 'Computadores', 'LENOVO-IP3.gif'),
('P002', 'Mouse Logitech', 8000000.00, 'tecnologia', 'images_2.jpg'),
('P004', 'Portátil Lenovo', 50000.00, 'Computadores', 'LENOVO-IP3.gif');


-- ==========================================
-- VERIFICAR TABLAS
-- ==========================================

SELECT * FROM usuarios;

SELECT * FROM productos;



