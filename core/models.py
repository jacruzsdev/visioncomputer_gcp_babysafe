
from django.db import models

class HistorialAnalisis(models.Model):
    # blank=True y null=True permiten que se guarde sin imagen
    imagen = models.ImageField(upload_to='analisis/', blank=True, null=True)
    mensaje_usuario = models.TextField(blank=True, null=True)
    respuesta_modelo = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        tipo = "Imagen" if self.imagen else "Texto"
        return f"Chat ({tipo}) - {self.fecha}"
