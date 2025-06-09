from django.urls import path
from .views import Communities

urlpatterns = [
    path('', Communities.as_view(), name='communities'),
]