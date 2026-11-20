# RentaCar Trujillo — Alquiler de vehículos

Aplicación web básica para gestionar el alquiler de vehículos, desarrollada con
**Python Flask**, **SQLite** y **Bootstrap 5** para el curso *Programación y Desarrollo Web* (UPRIT).

## Módulos

| Módulo | Funciones |
|---|---|
| **Vehículos** | Registrar (marca, modelo, placa, precio por día), listar, editar, eliminar y ver la disponibilidad (disponible / alquilado). |
| **Clientes** | Registrar (nombres, apellidos, DNI, teléfono), listar, editar y eliminar. |
| **Alquileres** | Registrar un alquiler eligiendo cliente y vehículo, con fecha de alquiler y de devolución. El costo total se calcula solo: `días × precio por día`. Listar, registrar la devolución y eliminar. |

## Ejecutar en tu equipo

```bash
python -m venv venv
venv\Scripts\activate          # En Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir <http://127.0.0.1:5000>. La base de datos `alquiler.db` se crea sola con `schema.sql`.

## Variables de entorno

| Variable | Uso | Valor por defecto |
|---|---|---|
| `SECRET_KEY` | Firma los mensajes de sesión | clave de desarrollo |
| `DATABASE_URL` | Ruta del archivo SQLite | `alquiler.db` |
| `FLASK_DEBUG` | `1` activa el modo debug (solo en desarrollo) | desactivado |
| `DATOS_DEMO` | `1` carga datos de ejemplo si la base está vacía | desactivado |

## Despliegue en Render

1. Subir el repositorio a GitHub.
2. En Render: **New → Web Service** y conectar el repositorio.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Variables de entorno: `SECRET_KEY` (cadena aleatoria) y `DATOS_DEMO=1`.

> En el plan gratuito de Render el disco es temporal: el archivo SQLite se reinicia
> cuando el servicio se reinicia. Por eso `DATOS_DEMO=1` vuelve a cargar los datos de ejemplo.

## Estructura

```
app.py              Rutas y lógica (Flask)
schema.sql          Tablas: vehiculos, clientes, alquileres
datos_demo.sql      Datos de ejemplo
requirements.txt    Dependencias
Procfile            Comando de inicio (gunicorn)
templates/          Plantillas HTML (Bootstrap)
static/             CSS y JavaScript
```

Ruta de salud para monitoreo: `/health`.

## Autor

Frank Edelin Piña Irarica — Ingeniería de Sistemas e Inteligencia Artificial, UPRIT.
