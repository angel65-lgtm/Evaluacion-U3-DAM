create database entregas_Paquexpress;

create table usuario (
    id_usuario int AUTO_INCREMENT NOT NULL PRIMARY KEY,
    usr_nombre varchar(100),
    usr_password varchar(255)
);

CREATE TABLE paquetes (
    id_paquete INT AUTO_INCREMENT PRIMARY KEY,
    pa_nombre VARCHAR(100),
    pa_descripcion TEXT,
    pa_dirOrigen VARCHAR(255),
    pa_dirDestino VARCHAR(255),
    pa_imagen VARCHAR(255),
    status ENUM('asignado', 'recolectado', 'entregado') DEFAULT 'asignado',
    usuario_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuario)
);

CREATE TABLE entregas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paquete_id INT,
    foto VARCHAR(255),
    latitud DECIMAL(10,8),
    longitud DECIMAL(11,8),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paquete_id) REFERENCES paquetes(id_paquete)
);