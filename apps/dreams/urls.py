from django.urls import path
from .views import AI_basic_call
urlpatterns = [
    path('ai/basic/', AI_basic_call.as_view(),name='simple call to deepseek')
]