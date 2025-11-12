# apps/users/urls.py
from django.urls import path
from .views import getSpecificUser, getAllUsers, getCurrentUser,CreatePsychologists,AllPsychologists
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', getAllUsers.as_view(), name='user-list'),
    path('me/', getCurrentUser.as_view(), name='current-user'),
    path('create-psychologist/',CreatePsychologists.as_view(),name='create-psychologist'), 
    path('psychologist/',AllPsychologists.as_view(),name="get psychologists"), # Nueva ruta para usuario actual
    path('<str:pk>/', getSpecificUser.as_view(), name='user-detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)