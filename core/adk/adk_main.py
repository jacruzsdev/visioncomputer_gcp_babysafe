import base64
import datetime
import os
import re
import uuid
import sys
from typing import List, Optional, Dict, Any
from zoneinfo import ZoneInfo

# Third-party imports
from django.core.files.uploadedfile import InMemoryUploadedFile
from google.cloud import aiplatform
from google.cloud import storage
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
from google.genai import types

# Google ADK imports
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# --- CONFIGURACIÓN Y CONSTANTES ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION")
ENDPOINT_ID = os.environ.get("VERTEX_MODEL_ID")
AGENT_MODEL = os.environ.get("AGENT_MODEL")
BUCKET_NAME = os.environ.get("BUCKET_NAME")

VERTEX_ENDPOINT_URI = (
    f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT_ID}"
)


# --- FUNCIONES DE UTILIDAD (GCS & BASE64) ---

def upload_django_file_to_gcs(
        file_obj: InMemoryUploadedFile,
        bucket_name: str,
        destination_folder: str = "uploads",
        project_id: Optional[str] = None
) -> Optional[str]:
    """
    Toma un archivo subido desde Django (InMemoryUploadedFile), lee sus bytes
    y lo sube directamente a GCS.

    Args:
        file_obj: El objeto proveniente de request.FILES['tu_input']
        bucket_name: Nombre del bucket en GCS.
        destination_folder: Carpeta destino dentro del bucket.
        project_id: ID del proyecto (opcional).

    Returns:
        str: La URI en formato 'gs://bucket/archivo' lista para Vertex AI, o None si falla.
    """

    try:
        # 1. OBTENER METADATOS DEL ARCHIVO DE DJANGO
        # file_obj.name suele ser "foto.jpg"
        original_filename = file_obj.name
        content_type = file_obj.content_type  # ej: "image/jpeg"

        # Extraer extensión de forma segura (ej: .jpg)
        _, extension = os.path.splitext(original_filename)
        if not extension:
            extension = ".jpg"  # Fallback

        # Quitamos el punto de la extensión para limpieza si es necesario,
        # aunque para el nombre de archivo solemos querer conservarlo.
        # Aquí generamos un nombre único: uuid + extensión original
        unique_filename = f"{uuid.uuid4()}{extension}"
        blob_path = f"{destination_folder}/{unique_filename}"

        # 2. LEER LOS BYTES
        # Aseguramos que el puntero del archivo esté al inicio (buena práctica en Django)
        file_obj.seek(0)
        file_data = file_obj.read()

        # 3. SUBIDA A GCS
        # Instanciar cliente
        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)

        # Subir bytes directamente (upload_from_string acepta bytes)
        blob.upload_from_string(
            data=file_data,
            content_type=content_type
        )

        # 4. RETORNAR URI
        gcs_uri = f"gs://{bucket_name}/{blob_path}"
        print(f"Imagen subida exitosamente: {gcs_uri}")
        return gcs_uri

    except Exception as e:
        print(f"Error subiendo archivo Django a GCS: {e}")
        return None


# --- HERRAMIENTAS (TOOLS) PARA EL AGENTE ---

def predict_image_object_detection_sample(
        gcs_source: str,
        project: str = PROJECT_ID,
        endpoint_id: str = ENDPOINT_ID,
        location: str = LOCATION,
        api_endpoint: str = "us-central1-aiplatform.googleapis.com",
) -> List[str]:
    """
    Descarga una imagen de GCS, la convierte a Base64 y detecta objetos en Vertex AI.
    """
    print(f"DEBUG: Procesando imagen desde {gcs_source}")

    # --- Paso 1: Descargar de GCS ---
    try:
        if not gcs_source.startswith("gs://"):
            return ["Error: La URI debe comenzar con gs://"]

        path_parts = gcs_source.replace("gs://", "").split("/", 1)
        bucket_name_local = path_parts[0]
        blob_name = path_parts[1]

        storage_client = storage.Client(project=project)
        bucket = storage_client.bucket(bucket_name_local)
        blob = bucket.blob(blob_name)

        # Descargar como bytes
        image_bytes = blob.download_as_bytes()

        # Convertir a Base64 string (UTF-8) para enviar en JSON
        encoded_content = base64.b64encode(image_bytes).decode("utf-8")

    except Exception as e:
        print(f"Error descargando de GCS: {e}")
        return []

    # --- Paso 2: Configurar Cliente Vertex AI ---
    client_options = {"api_endpoint": api_endpoint}
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    # --- Paso 3: Crear Instancia ---
    instance_dict = {"content": encoded_content}
    instance_value = Value()
    json_format.ParseDict(instance_dict, instance_value)

    instances = [instance_value]

    parameters_dict = {
        "confidence_threshold": 0.5,
        "max_predictions": 5,
    }
    parameters_value = Value()
    json_format.ParseDict(parameters_dict, parameters_value)

    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )

    # --- Paso 4: Predecir ---
    try:
        response = client.predict(
            endpoint=endpoint, instances=instances, parameters=parameters_value
        )

        predictions = response.predictions
        objects_detected = list()
        for prediction in predictions:
            pred_dict = dict(prediction)
            min_confidence = 0.4
            if "displayNames" and "confidences" in pred_dict:
                for indices in [i for i, x in enumerate(pred_dict["confidences"]) if x > min_confidence]:
                    objects_detected.append(pred_dict["displayNames"][indices])

        # Retornar lista única de objetos
        return list(set(objects_detected))

    except Exception as e:
        print(f"Error en Vertex AI Predict: {e}")
        return []


# --- DEFINICIÓN DEL AGENTE ---

# Instrucciones del sistema para el agente
BAYSAFE_INSTRUCTION = """
    Eres BaySafe, un experto en seguridad infantil automatizado.

    TU OBJETIVO: 
    Analizar una imagen recibida y generar un informe de seguridad para padres.

    TIENES UNA HERRAMIENTA OBLIGATORIA:
    - `predict_image_object_detection_sample`: Detecta qué objetos hay en la imagen.

    SIGUE ESTOS PASOS ESTRICTAMENTE:
    1. NUNCA SALUDES, TEN EN CUENTA QUE ESTA YA ES UNA CONVERSACIÓN EN CURSO
    1.  **DETECCIÓN:** Cuando recibas la imagen (base64 o URI), llama INMEDIATAMENTE a tu herramienta `predict_image_object_detection_sample`.
    2.  **ANÁLISIS INTERNO:** Una vez recibas la lista de objetos de la herramienta, clasifícalos mentalmente:
        * **PELIGROSO:** 'mesa_bordes', 'bateria', 'jarron', 'cadenilla', 'juguete_madera', 'Cojin_Suave', 'tela_colgante'.
        * **SEGURO:** Cualquier otro objeto.
    3.  **ANÁLISIS CRUZADOS:** Analiza la imagen en la URI de GCS para garantizar que los objetos detectados sí corresponden a los mencionados en la lista de objetos, elimina de la lista aquellos que realmente no están.
    3.  **RESPUESTA FINAL (OBLIGATORIA):**
        Genera una respuesta de texto natural dirigida al usuario. 
        NO devuelvas solo JSON. Habla con el usuario.

        Estructura tu respuesta así:
        - Un resumen de los objetos detectados.
        - Para cada objeto detectado, explica en una frase por qué es SEGURO o PELIGROSO.
        - Una conclusión final sobre si la zona es segura para un bebé.

    REGLA DE ORO:
    ¡Nunca termines la conversación después de llamar a la herramienta! 
    SIEMPRE debes usar la información que te devuelve la herramienta para escribir tu respuesta final.
"""

baysafe_agent = Agent(
    name="BaySafe_Unified",
    model=AGENT_MODEL,
    tools=[predict_image_object_detection_sample],
    description="Experto en seguridad infantil que detecta objetos y explica riesgos.",
    instruction=BAYSAFE_INSTRUCTION
)


# --- ORQUESTACIÓN Y EJECUCIÓN (RUNNER) ---

async def call_agent_async(query: str, runner: Runner, user_id: str, session_id: str) -> str:
    """Envía una consulta al agente y retorna la respuesta final."""
    print(f"\n>>> User Query: {query}")

    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break

    print(f"<<< Agent Response: {final_response_text}")
    return final_response_text


# ... (Todo el código anterior de importaciones, constantes, tools y definición de baysafe_agent) ...

# --- FUNCIÓN PÚBLICA PARA SER LLAMADA DESDE FUERA ---

async def run_safety_analysis(
        image_file: InMemoryUploadedFile,
        user_id: str = "default_user",
        session_id: str = "default_session"
) -> str:
    """
    Orquestador principal que recibe un archivo de Django y ejecuta el análisis.

    Args:
        image_file (InMemoryUploadedFile): Objeto del archivo recibido en request.FILES.
        user_id (str): ID del usuario para la sesión.
        session_id (str): ID de la sesión.

    Returns:
        str: La respuesta final del agente.
    """

    # 1. Validación básica
    if not image_file:
        return "Error: No se recibió un archivo válido."

    try:
        # 2. Subir a GCS (Directamente el objeto en memoria)
        # Nota: Ya no necesitamos convertir a base64 aquí.
        uri = upload_django_file_to_gcs(
            file_obj=image_file,
            bucket_name=BUCKET_NAME,
            project_id=PROJECT_ID
        )

        if not uri:
            return "Error: Falló la subida de la imagen a GCS."

        # 3. Configurar Sesión
        session_service = InMemorySessionService()
        app_name = "agents"

        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )

        # 4. Configurar Runner
        runner = Runner(
            agent=baysafe_agent,
            app_name=app_name,
            session_service=session_service
        )

        # 5. Ejecutar y retornar
        # El agente recibe la URI de GCS y hace su trabajo
        response_text = await call_agent_async(
            query=uri,
            runner=runner,
            user_id=user_id,
            session_id=session_id
        )

        return response_text

    except Exception as e:
        return f"Error crítico durante la ejecución del agente: {str(e)}"
