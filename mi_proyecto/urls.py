
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
