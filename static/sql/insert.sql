-- Insertar datos en la tabla sucursal
INSERT INTO sucursal (nombre, razon_social, ubicacion_escrita, ubicacion_googleMaps,telefono, estado,  logo) 
VALUES ('AUTOCAR ASOCATIE', ' S.A.', 'ACTUALIZAR INFORMACION DESDE EL SISTEMA', 'https://maps.app.goo.gl/rWHyYHcpwVUeAdbQ7', '123456789', '1', 'logo.jpg');

-- Insertar datos en la tabla sucursal

INSERT INTO horarios (id_sucursal, dia, hora_apertura, hora_cierre, estado)
VALUES
    ('1','Lunes', '09:00', '18:00', 1),
    ('1','Martes', '09:00', '18:00', 1),
    ('1','Miércoles', '09:00', '18:00', 1),
    ('1','Jueves', '09:00', '18:00', 1),
    ('1','Viernes', '09:00', '18:00', 1);

-- Insertar horarios para el fin de semana (sábado y domingo)
INSERT INTO horarios (id_sucursal, dia, hora_apertura, hora_cierre, estado)
VALUES
    ('1','Sábado', '10:00', '16:00', 1),
    ('1','Domingo', '10:00', '16:00', 2);
    


INSERT INTO servicios (nombre, descripcion, foto, realizacion, estado)
VALUES
  ('Lavado Básico', 'Lavado exterior del automóvil', 'lavado_basico.jpg', '1:00:00', 1),
  ('Lavado Premium', 'Lavado exterior e interior del automóvil', 'lavado_premium.jpg', '1:30:00', 1),
  ('Lavado de Motor', 'Limpieza del motor del automóvil', 'lavado_motor.jpg', '1:45:00', 1);


----- INSERT de precios de servicios
INSERT INTO precio_servicios (id_servicios, precio,fecha_registro, estado)
VALUES
  (1, 20.00,NOW(), 1), -- Precio del Lavado Básico: $20.00
  (2, 40.00,NOW(), 1), -- Precio del Lavado Premium: $40.00
  (3, 30.00,NOW(), 1); -- Precio del Lavado de Motor: $30.00

INSERT INTO tipo_venta (nombre, descripcion, estado) VALUES
    ('Sinpe', 'Pago mediante SINPE', 1),
    ('Planilla', 'Pago mediante planilla', 1),
    ('Efectivo', 'Pago en efectivo', 1),
    ('Tarjeta', 'Pago con tarjeta', 1);


-- Insertar datos en la tabla persona
INSERT INTO persona (nombre, correo, direccion, celular) 
VALUES ('Juan Perez', 'juan@admin.com', 'Calle 123, Ciudad', 123456789);

-- Insertar datos en la tabla persona_natural
INSERT INTO persona_natural (id_persona, apellido, cedula, fecha_nacimiento, genero, tipo_persona) 
VALUES (1, 'Perez', '123456789', '1990-01-01', 'M', 'Natural');

-- Insertar datos en la tabla trabajador
INSERT INTO trabajador (id_persona, codigo, foto, estado) 
VALUES (1, 'T123', '/static/img/Logo.png', 1);


-- Insertar datos en la tabla usuario
INSERT INTO usuario (id_persona, usuario, contraseña, estado) 
VALUES (1, 'juanperez', 'scrypt:32768:8:1$CmhEfUqnWfYuB28Q$c0a8a7840b1d97d63c380647f27d8963be262ed25e080edc1343403488cea251cbce57aebbe7591da559616f4ad41f7b5b0ea14db61c377e3f6a5fc974126d9b', 1);
-----Contraseña: 12345678

