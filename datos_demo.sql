-- Datos de ejemplo. Se cargan solo si DATOS_DEMO=1 y la base está vacía.
INSERT INTO vehiculos (marca, modelo, placa, precio_dia) VALUES
    ('Toyota', 'Yaris', 'T4K-512', 120.00),
    ('Hyundai', 'Tucson', 'BHR-734', 220.00),
    ('Kia', 'Rio', 'C7M-281', 110.00),
    ('Nissan', 'Frontier', 'T2P-946', 280.00),
    ('Suzuki', 'Swift', 'M3R-459', 98.50);

INSERT INTO clientes (nombres, apellidos, dni, telefono) VALUES
    ('María Fernanda', 'Rojas Castillo', '45871236', '948315627'),
    ('Luis Alberto', 'Vásquez Mendoza', '41526378', '976204183'),
    ('Jorge Enrique', 'Salinas Paredes', '43691572', '962847520'),
    ('Rosa Elena', 'Chávez Aguilar', '72154863', '931586274');

INSERT INTO alquileres (cliente_id, vehiculo_id, fecha_alquiler, fecha_devolucion, dias, costo_total, estado) VALUES
    (2, 3, '2026-11-09', '2026-11-13', 4, 440.00, 'devuelto'),
    (1, 2, '2026-11-18', '2026-11-25', 7, 1540.00, 'activo'),
    (4, 1, '2026-11-20', '2026-11-24', 4, 480.00, 'activo'),
    (3, 4, '2026-11-20', '2026-11-23', 3, 840.00, 'activo');
