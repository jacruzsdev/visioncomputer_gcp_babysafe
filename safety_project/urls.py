# safety_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Incluye las URLs de tu app principal
    path('', include('safety_detector.urls')), 
]