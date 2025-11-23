# safety_detector/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Nueva página de inicio (Home) que será el dashboard
    path('', views.home, name='home'), 
    
    # La página del detector (ahora bajo la ruta /detector/)
    path('detector/', views.predict_safety, name='predict_safety'),
    
    # La nueva vista de historial
    path('history/', views.history_view, name='history'),
    
    # La ruta para borrar el historial
    path('history/clear/', views.clear_history, name='clear_history'),
]