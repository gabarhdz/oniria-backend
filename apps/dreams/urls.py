from django.urls import path
from .views import deepseek_basic_call
urlpatterns = [
    path('ai/basic/', deepseek_basic_call.as_view(),name='simple call to deepseek ai')
]