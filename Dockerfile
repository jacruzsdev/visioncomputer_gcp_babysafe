# 1. Usar una imagen base de Python (estable y pequeña)
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE mi_proyecto.settings

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# 3. Copiar solo el archivo de requerimientos y luego instalar
# Esto aprovecha el cache de Docker si requirements.txt no cambia
COPY requirements.txt .
RUN pip install --no-cache-dir gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el código fuente completo del proyecto
# El .dockerignore evita copiar archivos innecesarios
COPY . .

# 5. Recolectar archivos estáticos (Django los prepara)
# Nota: La carpeta 'static' no debe estar en .dockerignore
RUN python manage.py collectstatic --noinput

# 6. Exponer el puerto en el que Gunicorn correrá
EXPOSE 8000

# 7. Comando para iniciar el servidor de producción (Gunicorn)
# Aquí debes reemplazar 'mi_proyecto' por el nombre de tu carpeta de configuración interna si es diferente (ej. 'miproyecto')
CMD ["gunicorn", "mi_proyecto.wsgi:application", "--bind", "0.0.0.0:8000"]