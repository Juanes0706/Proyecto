# 🚌 Sistema de Gestión TransMilenio - FastAPI

Este proyecto es una aplicación web desarrollada con **FastAPI**, diseñada para gestionar datos de buses y estaciones del sistema de transporte **TransMilenio**. Utiliza renderizado de plantillas HTML con **Jinja2**, almacenamiento y consultas a una base de datos relacional mediante **SQLAlchemy (Async)**, y está lista para ser desplegada en plataformas como **Render** o **Heroku**.

## ✨ Características principales

- ⚡ API moderna y rápida con FastAPI.
- 🧠 Uso de Pydantic para validación de datos.
- 🖼 Renderizado de HTML dinámico con Jinja2.
- 🔁 Gestión completa CRUD de Buses y Estaciones.
- 📂 Subida de archivos con soporte para imágenes.
- 🧵 Comunicación con la base de datos usando SQLAlchemy Async.
- 🧪 Documentación interactiva de la API (Swagger / Redoc).
- ☁️ Preparada para despliegue en Render/Heroku con `Procfile`.

---

## 🗂 Estructura del Proyecto
Proyecto/
│
├── app/
│ ├── database/
│ │ └── db.py # Configuración de la base de datos
│ ├── models/ # Modelos de SQLAlchemy
│ ├── operations/ # Lógica de negocio y funciones CRUD
│ ├── schemas/ # Esquemas Pydantic para validación
│ └── services/ # Funciones auxiliares
│
├── templates/ # Plantillas HTML con Jinja2
├── static/ # Archivos estáticos (CSS, JS, imágenes)
├── main.py # Punto de entrada principal
├── home.py # Rutas de frontend y backend
├── requirements.txt # Lista de dependencias
├── .env # Variables de entorno (no subir al repo)
└── Procfile # Para despliegue en Render/Heroku

---

## 📦 Instalación

```bash
git clone https://github.com/tu_usuario/tu_repo.git
cd Proyecto
python -m venv venv
source venv/bin/activate  # en Windows: venv\Scripts\activate
pip install -r requirements.txt

## 📌 Endpoints principales
## HTML
/ - Página principal (listado de buses y estaciones)

/agregar-bus, /editar-bus/{id}, /eliminar-bus/{id}

/agregar-estacion, /editar-estacion/{id}, /eliminar-estacion/{id}

## API
GET /api/buses - Lista todos los buses

POST /api/buses - Crea un nuevo bus

PUT /api/buses/{id} - Actualiza un bus

DELETE /api/buses/{id} - Elimina un bus

GET /api/estaciones

POST /api/estaciones

PUT /api/estaciones/{id}

DELETE /api/estaciones/{id}

## 🛠 Despliegue
En Render:
1. Configura variables de entorno en el panel.
2. Asegúrate de incluir el archivo Procfile:
3. Usa requirements.txt para gestionar dependencias.

## 🧪 Tecnologías usadas
1. FastAPI
2. Uvicorn
3. SQLAlchemy (async)
4. Jinja2
5. Pydantic
6. Render

## 📸 Soporte para Imágenes
El sistema permite subir imágenes asociadas a buses y estaciones. Las imágenes se almacenan en el servidor (o pueden integrarse con servicios como Supabase).

.

🧑‍💻 Autor
Juan Esteban Tovar Vargas
Contacto: tovarvargasjuanesteban@gmail.com

