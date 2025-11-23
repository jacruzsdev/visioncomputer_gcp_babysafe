import os
import sys

# --- LÓGICA DE RUTAS RELATIVAS (LA SOLUCIÓN) ---
# Esto asegura que el script trabaje DONDE ESTÁ EL ARCHIVO, no desde la terminal.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def encontrar_configuracion():
    """Busca automáticamente la carpeta interna que contiene settings.py"""
    items = os.listdir(BASE_DIR)
    for item in items:
        full_path = os.path.join(BASE_DIR, item)
        if os.path.isdir(full_path):
            if os.path.exists(os.path.join(full_path, 'settings.py')):
                return item
    return None

# Detectar nombre del proyecto
PROJECT_NAME = encontrar_configuracion()

if not PROJECT_NAME:
    print("❌ ERROR CRÍTICO: No encuentro la carpeta de configuración (la que tiene settings.py).")
    print(f"Asegúrate de poner este script AL LADO de manage.py en: {BASE_DIR}")
    sys.exit(1)

print(f"✅ Proyecto detectado: '{PROJECT_NAME}' en la ruta: {BASE_DIR}")

# --- CONTENIDOS ---

# 1. settings.py (Dinámico según el nombre encontrado)
SETTINGS_CONTENT = f"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-clave-de-prueba'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core', # <--- APP AGREGADA
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{PROJECT_NAME}.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = '{PROJECT_NAME}.wsgi.application'

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

AUTH_PASSWORD_VALIDATORS = [
    {{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',}},
    {{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',}},
    {{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',}},
    {{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',}},
]

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
"""

# 2. urls.py
URLS_CONTENT = """
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('clasificacion/', views.vista_clasificacion, name='clasificacion'),
    path('api/chat/', views.procesar_chat, name='procesar_chat'),
    path('historial/', views.historial, name='historial'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""

# 3. Models
MODELS_CONTENT = """
from django.db import models

class HistorialAnalisis(models.Model):
    imagen = models.ImageField(upload_to='analisis/')
    mensaje_usuario = models.TextField(blank=True, null=True)
    respuesta_modelo = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Análisis {self.id} - {self.fecha}"
"""

# 4. Views
VIEWS_CONTENT = """
from django.shortcuts import render
from django.http import JsonResponse
from .models import HistorialAnalisis
from django.views.decorators.csrf import csrf_exempt

def agente_vertex_ai(imagen_obj, texto_usuario):
    # TODO: Aquí irá tu código de Vertex AI
    print("Simulando llamada a Vertex AI...")
    return "Respuesta Simulada: Objeto detectado (Vertex no conectado)."

def home(request):
    context = {'autores': ['Autor 1', 'Autor 2'], 'app_info': 'App Django con IA'}
    return render(request, 'core/home.html', context)

def historial(request):
    registros = HistorialAnalisis.objects.all().order_by('-fecha')
    return render(request, 'core/historial.html', {'registros': registros})

def vista_clasificacion(request):
    return render(request, 'core/clasificacion.html')

@csrf_exempt
def procesar_chat(request):
    if request.method == 'POST':
        texto = request.POST.get('mensaje', '')
        imagen = request.FILES.get('imagen')
        if imagen:
            respuesta = agente_vertex_ai(imagen, texto)
            reg = HistorialAnalisis.objects.create(
                imagen=imagen, mensaje_usuario=texto, respuesta_modelo=respuesta
            )
            return JsonResponse({'status': 'ok', 'respuesta': respuesta, 'imagen_url': reg.imagen.url})
        return JsonResponse({'status': 'error', 'mensaje': 'Falta imagen'})
    return JsonResponse({'status': 'error'})
"""

# 5. HTML Templates (Minimizados para brevedad, funcionan igual)
BASE_HTML = """
<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>App IA</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{padding-top:20px;background:#f8f9fa}.chat-box{height:400px;overflow-y:scroll;background:white;padding:15px;border:1px solid #ccc;margin-bottom:15px}
.message{margin-bottom:10px;padding:10px;border-radius:10px}.user-msg{background:#e3f2fd;text-align:right;margin-left:20%}
.bot-msg{background:#f1f0f0;text-align:left;margin-right:20%}img.chat-img{max-width:200px;display:block;margin-top:5px}
</style></head><body><div class="container">{% block content %}{% endblock %}
<hr class="mt-5"><div class="d-flex justify-content-center gap-3 mb-5">
<a href="{% url 'home' %}" class="btn btn-outline-secondary">Home</a>
<a href="{% url 'clasificacion' %}" class="btn btn-outline-primary">Chat</a>
<a href="{% url 'historial' %}" class="btn btn-outline-info">Historial</a>
</div></div></body></html>
"""

HOME_HTML = """{% extends 'core/base.html' %}{% block content %}<div class="text-center mt-5">
<h1>Clasificador IA</h1><p>{{ app_info }}</p><div class="card mx-auto mt-4" style="max-width:500px">
<div class="card-header bg-dark text-white">Autores</div><ul class="list-group list-group-flush">
{% for a in autores %}<li class="list-group-item">{{ a }}</li>{% endfor %}</ul></div>
<div class="mt-5"><a href="{% url 'clasificacion' %}" class="btn btn-primary btn-lg">Ir al Chat</a></div></div>{% endblock %}"""

CLASIFICACION_HTML = """{% extends 'core/base.html' %}{% block content %}<h2 class="text-center">Chat IA</h2>
<div id="chat-box" class="chat-box"><div class="message bot-msg"><strong>IA:</strong> Sube imagen.</div></div>
<form id="chat-form" class="row g-2"><div class="col-8"><input type="text" id="m" class="form-control" placeholder="..."></div>
<div class="col-4"><input type="file" id="i" class="form-control" accept="image/*" required></div>
<div class="col-12"><button class="btn btn-success w-100">Enviar</button></div></form>
<script>
document.getElementById('chat-form').addEventListener('submit',async(e)=>{e.preventDefault();
const m=document.getElementById('m'),i=document.getElementById('i'),b=document.getElementById('chat-box');
if(!i.files[0])return;
b.innerHTML+=`<div class="message user-msg">Tú: ${m.value}</div>`;b.scrollTop=b.scrollHeight;
const fd=new FormData();fd.append('mensaje',m.value);fd.append('imagen',i.files[0]);
try{const r=await fetch("{% url 'procesar_chat' %}",{method:'POST',body:fd});const d=await r.json();
if(d.status=='ok'){b.innerHTML+=`<div class="message bot-msg">IA: ${d.respuesta}<br><img src="${d.imagen_url}" class="chat-img"></div>`;}
}catch(e){console.error(e);}m.value='';i.value='';b.scrollTop=b.scrollHeight;});
</script>{% endblock %}"""

HISTORIAL_HTML = """{% extends 'core/base.html' %}{% block content %}<h2 class="text-center">Historial</h2>
<table class="table"><thead><tr><th>Fecha</th><th>Img</th><th>Msg</th><th>IA</th></tr></thead><tbody>
{% for r in registros %}<tr><td>{{ r.fecha|date:"d/m H:i" }}</td><td><img src="{{ r.imagen.url }}" height="50"></td>
<td>{{ r.mensaje_usuario }}</td><td>{{ r.respuesta_modelo }}</td></tr>{% empty %}<tr><td colspan="4">Vacio</td></tr>
{% endfor %}</tbody></table>{% endblock %}"""

def instalar():
    # Rutas basadas en LA UBICACIÓN DEL SCRIPT (BASE_DIR)
    core_dir = os.path.join(BASE_DIR, 'core')
    media_dir = os.path.join(BASE_DIR, 'media')
    templates_dir = os.path.join(core_dir, 'templates', 'core')
    config_dir = os.path.join(BASE_DIR, PROJECT_NAME)

    print("📂 Creando carpetas relativas al script...")
    os.makedirs(core_dir, exist_ok=True)
    os.makedirs(media_dir, exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)

    print("📝 Escribiendo archivos de la app Core...")
    # Archivos core
    open(os.path.join(core_dir, '__init__.py'), 'w').close()
    with open(os.path.join(core_dir, 'admin.py'), 'w') as f: f.write("from django.contrib import admin\nfrom .models import HistorialAnalisis\nadmin.site.register(HistorialAnalisis)")
    with open(os.path.join(core_dir, 'apps.py'), 'w') as f: f.write("from django.apps import AppConfig\nclass CoreConfig(AppConfig):\n default_auto_field='django.db.models.BigAutoField'\n name='core'")
    with open(os.path.join(core_dir, 'models.py'), 'w', encoding='utf-8') as f: f.write(MODELS_CONTENT)
    with open(os.path.join(core_dir, 'views.py'), 'w', encoding='utf-8') as f: f.write(VIEWS_CONTENT)

    print("🎨 Escribiendo Templates...")
    with open(os.path.join(templates_dir, 'base.html'), 'w', encoding='utf-8') as f: f.write(BASE_HTML)
    with open(os.path.join(templates_dir, 'home.html'), 'w', encoding='utf-8') as f: f.write(HOME_HTML)
    with open(os.path.join(templates_dir, 'clasificacion.html'), 'w', encoding='utf-8') as f: f.write(CLASIFICACION_HTML)
    with open(os.path.join(templates_dir, 'historial.html'), 'w', encoding='utf-8') as f: f.write(HISTORIAL_HTML)

    print(f"⚙️ Configurando '{PROJECT_NAME}/settings.py' y 'urls.py'...")
    with open(os.path.join(config_dir, 'settings.py'), 'w', encoding='utf-8') as f: f.write(SETTINGS_CONTENT)
    with open(os.path.join(config_dir, 'urls.py'), 'w', encoding='utf-8') as f: f.write(URLS_CONTENT)

    print("\n✅ ¡Instalación Completada!")
    print("Ahora ejecuta en tu terminal (asegúrate de estar en la carpeta del script):")
    print("1. python manage.py makemigrations core")
    print("2. python manage.py migrate")
    print("3. python manage.py runserver")

if __name__ == "__main__":
    instalar()