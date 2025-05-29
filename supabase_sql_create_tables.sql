CREATE TABLE buses (
    id SERIAL PRIMARY KEY,
    nombre_bus VARCHAR(255),
    tipo VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    imagen VARCHAR(255) -- storing jpg image filename or URL
);

CREATE TABLE estaciones (
    id SERIAL PRIMARY KEY,
    nombre_estacion VARCHAR(255) UNIQUE,
    localidad VARCHAR(255),
    rutas_asociadas TEXT,
    activo BOOLEAN DEFAULT TRUE,
    imagen VARCHAR(255) -- storing jpg image filename or URL
);
