from django.urls import path
from .views import AllPsychologists,SpecificPsychologist,AiTraining

urlpatterns = [ 
    path('/', AllPsychologists.as_view(),name="get-all-psychologists"),
    path('/<str:pk>/', SpecificPsychologist.as_view(),name="get-psychologist"),
    path('train-ai/', AiTraining.as_view(),name="train-ai")
    ]