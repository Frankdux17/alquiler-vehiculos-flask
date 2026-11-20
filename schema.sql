CREATE TABLE IF NOT EXISTS vehiculos (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    marca      TEXT NOT NULL,
    modelo     TEXT NOT NULL,
    placa      TEXT NOT NULL UNIQUE,
    precio_dia REAL NOT NULL CHECK (precio_dia > 0)
);

CREATE TABLE IF NOT EXISTS clientes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombres   TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    dni       TEXT NOT NULL UNIQUE,
    telefono  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alquileres (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id       INTEGER NOT NULL REFERENCES clientes(id),
    vehiculo_id      INTEGER NOT NULL REFERENCES vehiculos(id),
    fecha_alquiler   TEXT NOT NULL,
    fecha_devolucion TEXT NOT NULL,
    dias             INTEGER NOT NULL,
    costo_total      REAL NOT NULL,
    estado           TEXT NOT NULL DEFAULT 'activo'  -- 'activo' o 'devuelto'
);
