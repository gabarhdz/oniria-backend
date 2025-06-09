from django.urls import path
from .views import getSpecificUser, getAllUsers

urlpatterns = [
    path('', getAllUsers.as_view(), name='user-list'),
    path('<str:pk>/', getSpecificUser.as_view(), name='user-detail'),
]