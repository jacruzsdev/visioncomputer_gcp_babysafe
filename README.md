# Baby Safe - Computer Vision

[<img width="403" height="141" alt="image" src="https://github.com/user-attachments/assets/321c115e-96f0-4b01-9b9e-2eb859b061c7" />](https://creativecommons.org/licenses/by-nc-sa/4.0/)

# 👶 VisionComputer GCP BabySafe

**Baby Safe** es una aplicación web inteligente diseñada para analizar la seguridad de entornos infantiles. Utiliza modelos de **Computer Vision (AutoML)** entrenados en **Google Cloud Vertex AI** y orquestados mediante el **Google Agent Development Kit (ADK)** para detectar objetos peligrosos y seguros en imágenes subidas por el usuario.

El sistema simula un asistente experto ("BaySafe") que no solo detecta objetos, sino que razona sobre ellos para entregar un reporte de seguridad a los padres.

## 🚀 Arquitectura y Tecnologías

El proyecto sigue una arquitectura moderna basada en la nube:

  * **Backend:** Django 5.2.
  * **IA & Orquestación:**
      * **Google Agent Development Kit (ADK):** Gestiona el flujo de conversación y el razonamiento del agente (`BaySafe_Unified`).
      * **Vertex AI (AutoML):** Modelo de detección de objetos personalizado.
      * **Google GenAI:** Modelo de lenguaje (LLM) para generar la respuesta natural.
  * **Almacenamiento:** Google Cloud Storage (para imágenes temporales de análisis).
  * **Frontend:** HTML5 + JavaScript (con integración a Firebase Firestore para historial).

## 📋 Pre-requisitos

1.  **Python 3.11+**.
2.  Un proyecto en **Google Cloud Platform** con las siguientes APIs habilitadas:
      * Vertex AI API.
      * Cloud Storage API.
3.  **Cuenta de Servicio (Service Account):**
      * Debe tener permisos para escribir en Storage y predecir en Vertex AI.
      * Descarga el archivo JSON de credenciales.
4.  **Modelo Entrenado:** Un modelo de *Object Detection* desplegado en un Endpoint de Vertex AI.

## ⚙️ Instalación

1.  **Clonar el repositorio:**

<!-- end list -->

```bash
git clone https://github.com/jacruzsdev/visioncomputer_gcp_babysafe.git
cd visioncomputer_gcp_babysafe
```

2.  **Crear entorno virtual e instalar dependencias:**

<!-- end list -->

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

> **Nota:** El archivo `requirements.txt` incluye librerías críticas como `google-adk`, `google-cloud-aiplatform` y `django`.

## 🔐 Configuración de Variables de Entorno (.env)

Basado en el análisis del código (`settings.py` y `adk_main.py`), es **obligatorio** crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```ini
# --- Configuración General de GCP ---
GOOGLE_CLOUD_PROJECT=tu-id-de-proyecto-gcp
GOOGLE_CLOUD_LOCATION=us-central1

# --- Configuración del Modelo Vertex AI (Object Detection) ---
# ID del Endpoint donde está desplegado tu modelo de AutoML
VERTEX_MODEL_ID=1234567890123456789

# --- Configuración del Agente ADK ---
# Modelo LLM que usará el agente para razonar (ej. gemini-1.5-pro)
AGENT_MODEL=gemini-2.5-flash-001

# --- Almacenamiento ---
# Nombre del bucket donde se subirán las imágenes para análisis
BUCKET_NAME=nombre-de-tu-bucket-gcp

# --- Autenticación (Recomendado) ---
# Ruta local a tu archivo JSON de credenciales de servicio
GOOGLE_APPLICATION_CREDENTIALS=./credenciales/tu-archivo-key.json
```

## ▶️ Ejecución

1.  Aplica las migraciones iniciales de Django:

    ```bash
    python manage.py migrate
    ```

2.  Inicia el servidor de desarrollo:

    ```bash
    python manage.py runserver
    ```

3.  Accede a la aplicación en `http://127.0.0.1:8000`.

## 🧠 Lógica del Agente (BaySafe)

El núcleo de la IA se encuentra en `core/adk/adk_main.py`. El flujo es el siguiente:

1.  El usuario sube una imagen en el chat.
2.  Django sube la imagen a **Google Cloud Storage**.
3.  El **Agente ADK** recibe la URI de la imagen (`gs://...`).
4.  El agente invoca la herramienta `predict_image_object_detection_sample`.
5.  **Vertex AI** devuelve los objetos detectados (ej: `mesa_bordes`, `juguete_madera`, `bateria`).
6.  El Agente clasifica los objetos en:
      * 🔴 **Peligrosos:** *mesa\_bordes, bateria, jarron, cadenilla, etc.*
      * 🟢 **Seguros:** *Otros objetos.*
7.  Se genera una respuesta en lenguaje natural explicando los riesgos al usuario.

## 📂 Estructura del Proyecto

```text
visioncomputer_gcp_babysafe/
├── core/
│   ├── adk/
│   │   └── adk_main.py       # Lógica principal del Agente y conexión con Vertex
│   ├── templates/core/
│   │   └── clasificacion.html # Interfaz de chat (JS + Firebase)
│   └── views.py              # Controladores de Django (Endpoints)
├── mi_proyecto/
│   ├── settings.py           # Configuración de Django y carga de .env
│   └── wsgi.py
├── requirements.txt          # Dependencias del proyecto
├── .env                      # Variables de entorno (NO INCLUIDO EN REPO)
└── manage.py
```

## 👥 Autores

* **Joaquín Iván Barrera Lozada - jbarrera17@unisalle.edu.co**

* **Jesus Andres Cruz Sanabria - jcruz47@unisalle.edu.co**

-----

*Este proyecto es parte de una implementación académica para demostrar el uso de IA Generativa y Visión por Computadora en la nube.*
