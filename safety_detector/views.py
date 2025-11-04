# safety_detector/views.py (Versión Ultra-Segura: GET solo renderiza)
import os
import base64
from django.shortcuts import render, redirect
# from google.cloud import aiplatform  <-- Importación tardía
from datetime import datetime 

# --- CONFIGURACIÓN GLOBAL (Debe estar aquí) ---
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "") 
REGION = os.environ.get("GCP_REGION", "") 
ENDPOINT_ID = os.environ.get("VERTEX_ENDPOINT_ID", "") 
HISTORY_SESSION_KEY = 'safety_history'
# ----------------------------------------------

def home(request):
    """Renderiza la página de inicio o el dashboard."""
    return render(request, 'detector/home.html')

def predict_safety(request):
    """
    Maneja la carga de imágenes, la predicción y el guardado del historial.
    La solicitud GET solo renderiza el formulario para aislar el error.
    """
    
    # LÓGICA CRÍTICA: MANEJO DE GET
    if request.method == 'GET':
        # Verificación del estado de la IA para mostrar una advertencia en la interfaz
        if not (PROJECT_ID and REGION and ENDPOINT_ID):
            prediction_result = "⚠️ Advertencia: Los recursos de Vertex AI aún no están configurados. La detección está en MODO SIMULACIÓN."
        else:
            prediction_result = None # No hay resultado si no se ha enviado nada
        
        # Simplemente renderizamos la plantilla con los valores iniciales.
        return render(request, 'detector/index.html', {
            'is_safe': None,
            'prediction_result': prediction_result
        })

    # LÓGICA CRÍTICA: MANEJO DE POST
    if request.method == 'POST':
        
        # --- Lógica de Sesión (Se ejecuta solo en POST) ---
        if HISTORY_SESSION_KEY not in request.session:
            request.session[HISTORY_SESSION_KEY] = []
            request.session.modified = True 

        # ... (Toda la lógica de Vertex AI, simulación, guardado de historial) ...
        # ... (Mantén toda la lógica de POST que tenías en tu versión anterior) ...
        
        # Código de POST (Ejemplo simplificado, usa tu código POST completo aquí)
        is_safe = False
        prediction_result = "POST: Resultado de prueba."
        image_b64 = None
        
        try:
            # Lógica completa de POST (incluyendo la codificación base64 y Vertex AI/Simulación)
            image_file = request.FILES['image_file']
            image_bytes = image_file.read()
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')

            # SIMULACIÓN (porque la IA no está configurada)
            is_safe = True
            prediction_result = "✅ SIMULACIÓN: Objeto clasificado como seguro. Configure Vertex AI para resultados reales."

            # Guardar en historial
            history_entry = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'is_safe': is_safe,
                'result': prediction_result,
                'image_b64': image_b64,
            }
            request.session[HISTORY_SESSION_KEY].insert(0, history_entry)
            request.session.modified = True

        except Exception as e:
            prediction_result = f"Error durante POST: {e}"
            is_safe = False
            
        return render(request, 'detector/index.html', {
            'is_safe': is_safe,
            'prediction_result': prediction_result
        })

# La vista de historial y borrar historial no cambian.
def history_view(request):
    """Muestra el historial de la sesión actual."""
    history = request.session.get(HISTORY_SESSION_KEY, [])
    return render(request, 'detector/history.html', {'history': history})

def clear_history(request):
    """Borra el historial y redirige al home."""
    if HISTORY_SESSION_KEY in request.session:
        del request.session[HISTORY_SESSION_KEY]
    return redirect('home')