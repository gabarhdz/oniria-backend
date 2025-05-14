from django.urls import path
from .views import getSpecificUser, getAllUsers

urlpatterns = [
    path('user/all/', getAllUsers.as_view(), name='user-list'),
    path('user/<str:pk>/', getSpecificUser.as_view(), name='user-detail'),
]