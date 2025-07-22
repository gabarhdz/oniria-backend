from django.urls import path
from .views import getSpecificUser, getAllUsers
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', getAllUsers.as_view(), name='user-list'),
    path('<str:pk>/', getSpecificUser.as_view(), name='user-detail'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


