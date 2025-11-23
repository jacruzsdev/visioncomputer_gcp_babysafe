import asyncio
import os

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .adk.adk_main import run_safety_analysis
import json


# --- AGENTE VERTEX AI (PLACEHOLDER) ---
def agente_vertex_ai(imagen_presente, texto_usuario, imagen=None):
    """
    Simulación del agente IA.
    """
    if imagen:
        # Lógica si hay imagen
        print(type(imagen))
        imagen_a_analizar = imagen  # Asegúrate que esta imagen exista
        usuario = "padre_preocupado_1"
        sesion = "analisis_001"

        print(f"--- Iniciando análisis para {imagen_a_analizar} ---")

        # Llamamos a la función asíncrona del módulo
        resultado = asyncio.run(run_safety_analysis(
            image_file=imagen_a_analizar,
            user_id=usuario,
            session_id=sesion
        ))
        print("\n--- REPORTE DE SEGURIDAD ---")
        print(resultado)
        print("-----------------------------")
        return resultado
    else:
        # Lógica si es solo conversación
        return f"Con gusto! por favor carga una imagen para que comencemos"


def home(request):
    context = {
        'autores': ['Barrera Lozada Joaquín Iván - Grupo 1', 'Cruz Sanabria Jesus Andres - Grupo 2'],
        'app_info': 'Aplicación de clasificación de imágenes con IA - Baby Safe'
    }
    return render(request, 'core/home.html', context)

def historial(request):
    # La lógica de carga del historial se movió a historial.html (JavaScript)
    return render(request, 'core/historial.html')

def vista_clasificacion(request):
    # La lógica de carga del chat se movió a clasificacion.html (JavaScript)
    return render(request, 'core/clasificacion.html')

@csrf_exempt
def procesar_chat(request):
    """
    API endpoint de Django que simula la respuesta de la IA.
    """
    if request.method == 'POST':
        # El frontend solo envía texto plano y un flag 'tiene_imagen'
        print(request.POST.get)

        texto = request.POST.get('mensaje', '')
        tiene_imagen = request.POST.get('tiene_imagen', 'False')

        if not texto and tiene_imagen == 'False':
            return JsonResponse({'status': 'error', 'mensaje': 'Contenido vacío'})

        # 1. Procesar con IA
        if tiene_imagen == "True":
            archivo_imagen = request.FILES.get("imagen")
            print(archivo_imagen)
            respuesta_ia = agente_vertex_ai(tiene_imagen, texto, archivo_imagen)
        else:
            respuesta_ia = agente_vertex_ai(tiene_imagen, texto)

        return JsonResponse({
            'status': 'ok',
            'respuesta': respuesta_ia,
        })

    return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido'})