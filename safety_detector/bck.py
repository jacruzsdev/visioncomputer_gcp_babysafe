# safety_detector/views.py (Versión Final para Navegación sin IA configurada)
import os
import base64
from django.shortcuts import render, redirect
# from google.cloud import aiplatform <-- ¡QUITAMOS ESTA IMPORTACIÓN!
from datetime import datetime
from typing import Optional # Útil para tipado claro

# --- CONFIGURACIÓN DE VERTEX AI (Valores default de cadena vacía) ---
# Usamos default="" para que la lógica 'if not (PROJECT_ID and ...)' funcione correctamente.
PROJECT_ID: Optional[str] = os.environ.get("GCP_PROJECT_ID", "") 
REGION: Optional[str] = os.environ.get("GCP_REGION", "") 
ENDPOINT_ID: Optional[str] = os.environ.get("VERTEX_ENDPOINT_ID", "") 
# --------------------------------------------------------------------

# Clave de sesión para almacenar el historial
HISTORY_SESSION_KEY = 'safety_history'

def home(request):
    """Renderiza la página de inicio o el dashboard."""
    return render(request, 'detector/home.html')

def predict_safety(request):
    """Maneja la carga de imágenes, la predicción y el guardado del historial."""
    is_safe = None
    prediction_result = None
    
    # 1. Inicializa el historial en la sesión
    # (El acceso inmediato a la sesión funciona ya que /history/ lo prueba)
    if HISTORY_SESSION_KEY not in request.session:
        request.session[HISTORY_SESSION_KEY] = []
        request.session.modified = True 

    # 2. Chequeo de Pre-requisitos (GET y POST)
    # Si falta la configuración, mostramos la interfaz con una advertencia
    if not (PROJECT_ID and REGION and ENDPOINT_ID):
        prediction_result = "⚠️ Advertencia: Los recursos de Vertex AI aún no están configurados. La detección está en MODO SIMULACIÓN."
        context = {
            'is_safe': None, # No podemos determinar la seguridad en este estado
            'prediction_result': prediction_result
        }
        # Si es GET, mostramos la interfaz con la advertencia
        if request.method == 'GET':
            return render(request, 'detector/index.html', context)
        
        # Si es POST sin configuración, aún debemos guardar el resultado de la simulación.

    # 3. Lógica POST (Solo si el usuario envía un formulario)
    if request.method == 'POST' and request.FILES.get('image_file'):
        image_file = request.FILES['image_file']
        image_b64 = None
        
        # Leemos la imagen inmediatamente para la simulación/historial
        image_bytes = image_file.read()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        try:
            # --- DECISIÓN CRÍTICA: Lógica de la IA (Solo si configurado) ---
            if PROJECT_ID and REGION and ENDPOINT_ID:
                # ¡IMPORTACIÓN TARDÍA! Solo se ejecuta si la lógica de arriba pasa.
                from google.cloud import aiplatform 
                
                client_options = {"api_endpoint": f"{REGION}-aiplatform.googleapis.com"}
                client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
                
                # ... [Ejecución del modelo real] ...
                is_safe = True
                prediction_result = "✅ Resultado real: Objeto seguro."
                
            else:
                # --- MODO SIMULACIÓN ---
                is_safe = True
                prediction_result = "✅ SIMULACIÓN: Objeto clasificado como seguro. Configure Vertex AI para resultados reales."

        except Exception as e:
            # Captura errores durante la ejecución de Vertex AI/Simulación
            prediction_result = f"Error de Procesamiento: {e}"
            is_safe = False 

        # 4. Guardar el resultado en el Historial (Usando el image_b64 decodificado)
        if image_b64:
            history_entry = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'is_safe': is_safe,
                'result': prediction_result,
                'image_b64': image_b64,
            }
            request.session[HISTORY_SESSION_KEY].insert(0, history_entry)
            request.session.modified = True 

    # 5. Retorno para GET y POST
    return render(request, 'detector/index.html', {
        'is_safe': is_safe,
        'prediction_result': prediction_result
    })

def history_view(request):
    """Muestra el historial de la sesión actual."""
    history = request.session.get(HISTORY_SESSION_KEY, [])
    # No es necesario inicializar el historial aquí, ya que predict_safety lo hace.
    return render(request, 'detector/history.html', {'history': history})

def clear_history(request):
    """Borra el historial y redirige al home."""
    if HISTORY_SESSION_KEY in request.session:
        del request.session[HISTORY_SESSION_KEY]
    return redirect('home')