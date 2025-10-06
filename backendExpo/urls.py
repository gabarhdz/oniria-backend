from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.users.chat_views import ChatAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/psychologists/', include('apps.psychologists.urls')),
    path('api/communities/', include('apps.community.urls')),   
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('api/dreams/', include('apps.dreams.urls')),
    # Nuevo endpoint para el chat
    path('api/chat/', ChatAPIView.as_view(), name='chat-api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)