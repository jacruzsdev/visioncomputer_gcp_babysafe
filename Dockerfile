# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establece variables de entorno
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE safety_project.settings

# Crea un directorio de trabajo y copia los archivos
WORKDIR /app
COPY requirements.txt /app/

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . /app/

# Expón el puerto que usará Cloud Run
# Cloud Run inyecta la variable de entorno PORT, pero Gunicorn necesita saber el puerto por defecto
ENV PORT 8080

# Comando para correr Gunicorn (sustituye tu 'safety_project.wsgi' por el path correcto)
CMD exec gunicorn --bind 0.0.0.0:$PORT safety_project.wsgi