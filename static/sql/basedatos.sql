CREATE TABLE sucursal(
    id SERIAL PRIMARY KEY,
    nombre VARCHAR (250) NOT NULL,
    razon_social VARCHAR(250),
    ubicacion_escrita VARCHAR(250),
    ubicacion_googleMaps VARCHAR(500),
    telefono INTEGER,
    estado INTEGER,
    logo VARCHAR(250)
    
);
CREATE TABLE persona (
 id SERIAL PRIMARY KEY,
 nombre VARCHAR(150) NOT NULL,
 correo VARCHAR(150) NOT NULL,
 direccion VARCHAR(250),
 celular BIGINT UNIQUE
);
CREATE TABLE persona_natural (
    id SERIAL PRIMARY KEY,
    id_persona INTEGER REFERENCES persona(id),
    apellido VARCHAR(250) NOT NULL,
    cedula VARCHAR(80),
    fecha_nacimiento DATE,
    genero CHAR,
    tipo_persona VARCHAR(50)
);

CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    id_persona INTEGER REFERENCES persona(id),
    codigo VARCHAR(50),
    tipo_cliente VARCHAR(250) NOT NULL,
    foto VARCHAR(250) ,
    estado INTEGER
);


CREATE TABLE trabajador
(
    id SERIAL primary key,
    id_persona INTEGER REFERENCES persona(id),
    codigo VARCHAR(50) NOT NULL,
    foto VARCHAR(250) ,
    estado INTEGER 
);



CREATE TABLE producto
(
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    descripcion varchar(250) NOT NULL,
    logo VARCHAR(250),
    tipo INTEGER,
    estado INTEGER
);
CREATE TABLE precio(
    id SERIAL PRIMARY KEY,
    id_producto INTEGER REFERENCES producto(id),
    precio NUMERIC(10,2) NOT NULL,
    fecha_registro DATE NOT NUll,
    estado INTEGER
);

CREATE TABLE lote_producto
(
    id SERIAL PRIMARY KEY,
    id_producto INTEGER REFERENCES producto(id),
    numero_lote VARCHAR(50) NOT NULL,
    fecha_vencimiento DATE,
    fecha_registro DATE NOT NUll,
    cantidad INTEGER NOT NULL,
    estado INTEGER
);



CREATE TABLE solicitud_producto(
    id serial PRIMARY KEY,
    id_trabajador INTEGER REFERENCES trabajador(id),
    fecha_solicitud DATE,
    motivo VARCHAR(5000),
    estado INTEGER
);

CREATE TABLE detalle_solicitud(
    id SERIAL PRIMARY KEY,
    id_solicitud INTEGER REFERENCES solicitud_producto(id),
    id_producto INTEGER REFERENCES producto(id),
    Cantidad INTEGER NOT NULL
);

CREATE TABLE movimiento_inventario
(
    id SERIAL PRIMARY KEY,
    id_lote INTEGER REFERENCES lote_producto(id),
    tipo_movimiento VARCHAR(250) NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE horarios(
    id SERIAL PRIMARY KEY,
  	id_sucursal INTEGER REFERENCES sucursal(id),
    dia VARCHAR(255) NOT NULL,
    hora_apertura TIME,
    hora_cierre TIME ,
    estado INTEGER NOT NULL
);

CREATE TABLE categoria(
    id SERIAL PRIMARY KEY,
    nombre varchar not null,
    descripcion varchar,
    estado INTEGER
);

CREATE TABLE servicios(
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    descripcion VARCHAR(250),
    foto VARCHAR(250),
    realizacion TIME NOT NUll,
    estado INTEGER,
    id_categoria INTEGER REFERENCES categoria(id)
);

CREATE TABLE precio_servicios(
    id SERIAL PRIMARY KEY,
    id_servicios INTEGER REFERENCES servicios(id),
    precio NUMERIC(10,2) NOT NULL,
    fecha_registro DATE NOT NUll,
    estado INTEGER
);
CREATE TABLE tipo_venta (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(250) NOT NUll,
    descripcion VARCHAR(250),
    estado INTEGER
);

CREATE TABLE reservacion(
    id SERIAL PRIMARY KEY,
    idcliente INTEGER REFERENCES clientes(id),
    idservicio INTEGER REFERENCES servicios(id),
    idevento_calendar VARCHAR(250),
    codigo VARCHAR(50) UNIQUE,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME,
    subtotal DECIMAL(10,2),
    estado INTEGER,
    id_metodo_pago INTEGER REFERENCES tipo_venta(id) -- Nueva columna
);


CREATE TABLE venta(
    id SERIAL PRIMARY KEY,
    id_tipo INTEGER REFERENCES tipo_venta(id),
    id_cliente INTEGER REFERENCES clientes(id),
    codigo VARCHAR(255),
    fecha DATE,
    descuento NUMERIC NOT NULL,
    total NUMERIC NOT NULL,
    estado INTEGER
);


CREATE TABLE detalle_venta
(
    id SERIAL PRIMARY KEY,
    id_venta INTEGER REFERENCES venta(id),
    id_servicio INTEGER REFERENCES servicios(id),
    precio_unitario NUMERIC NOT NULL,
    cantidad INTEGER,
    subtotal numeric NOT NULL
);

CREATE TABLE detalle_venta_cita
(
    id SERIAL PRIMARY KEY,
    id_venta INTEGER REFERENCES venta(id),
    id_reserva INTEGER REFERENCES reservacion(id),
    precio_unitario NUMERIC NOT NULL,
    subtotal numeric NOT NULL
);




CREATE TABLE venta_productos(
    id SERIAL PRIMARY KEY,
    id_venta INTEGER REFERENCES venta(id),
    id_producto INTEGER REFERENCES producto(id),
    precio_unitario NUMERIC NOT NULL,
    cantidad INTEGER,
    subtotal numeric NOT NUll 
);



CREATE TABLE usuario
(
    id SERIAL PRIMARY KEY,
    id_persona INTEGER REFERENCES persona(id),
    rol INTEGER,
    usuario VARCHAR(200) NOT NULL,
    contraseña VARCHAR(250) NOT NULL,
    estado INTEGER 
);

CREATE TABLE notificarproducto(
    id SERIAL PRIMARY KEY,
    id_producto INTEGER REFERENCES producto(id),
    telefono VARCHAR(50),
    estado INTEGER 
);


CREATE TABLE comprobantes(
    id SERIAL PRIMARY KEY,
    telefono VARCHAR(50) NOT NULL,
    comprobante TEXT,
    fecha DATE,
    estado INTEGER
);