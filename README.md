# 🚌 Sistema de Gestión TransMilenio - FastAPI

Este proyecto es una aplicación web desarrollada con **FastAPI**, diseñada para gestionar datos de buses y estaciones del sistema de transporte **TransMilenio**. Utiliza renderizado de plantillas HTML con **Jinja2**, almacenamiento y consultas a una base de datos relacional mediante **SQLAlchemy (Async)**, y está lista para ser desplegada en plataformas como **Render**.

---

## ✨ Características principales

- ⚡ API moderna y rápida con FastAPI.
- 🧠 Validación robusta con Pydantic.
- 🖼 Renderizado de HTML dinámico con Jinja2.
- 🔁 Gestión completa CRUD de Buses y Estaciones.
- 📂 Soporte para subida de imágenes.
- 🧵 Comunicación con la base de datos usando SQLAlchemy Async.
- 🧪 Documentación automática con Swagger y Redoc.
- ☁️ Lista para despliegue con `Procfile`.

---

## 🗂 Estructura del Proyecto

│
├── app/
│ ├── database/
│ │ └── db.py # Configuración de la base de datos
│ ├── models/ # Modelos de SQLAlchemy
│ ├── operations/ # Funciones CRUD
│ ├── schemas/ # Esquemas de validación con Pydantic
│ └── services/ # Funciones auxiliares
│
├── templates/ # Plantillas HTML con Jinja2
├── static/ # Archivos estáticos (CSS, JS, imágenes)
├── main.py # Punto de entrada principal
├── home.py # Rutas frontend y backend
├── requirements.txt # Dependencias del proyecto
├── .env # Variables de entorno (no subir al repo)
└── Procfile # Configuración para despliegue


---

## 📦 Instalación

```bash
git clone https://github.com/juanes0706/Proyecto
cd Proyecto
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

