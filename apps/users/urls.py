# apps/users/urls.py
from django.urls import path
from .views import getSpecificUser, getAllUsers, getCurrentUser,CreatePsychologists,AllPsychologists,SpecificPsychologist
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', getAllUsers.as_view(), name='user-list'),
    path('me/', getCurrentUser.as_view(), name='current-user'),
    path('create-psychologist/',CreatePsychologists.as_view(),name='create-psychologist'), 
    path('psychologist/',AllPsychologists.as_view(),name="get psychologists"),
    path('psychologist/<str:pk>/',SpecificPsychologist.as_view()), # Nueva ruta para usuario actual
    path('<str:pk>/', getSpecificUser.as_view(), name='user-detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)