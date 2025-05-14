from django.urls import path
from .views import AllPsychologists

urlpatterns = [
    path('psychologists/', AllPsychologists.as_view(),name="get-all-psychologists")
]