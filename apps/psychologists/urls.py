from django.urls import path
from .views import AllPsychologists,SpecificPsychologist

urlpatterns = [
    path('psychologists/', AllPsychologists.as_view(),name="get-all-psychologists"),
    path('psychologists/<str:pk>/', SpecificPsychologist.as_view(),name="get-psychologist")
]