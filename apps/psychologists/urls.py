from django.urls import path
from .views import AllPsychologists,SpecificPsychologist

urlpatterns = [
    path('/', AllPsychologists.as_view(),name="get-all-psychologists"),
    path('/<str:pk>/', SpecificPsychologist.as_view(),name="get-psychologist")
]