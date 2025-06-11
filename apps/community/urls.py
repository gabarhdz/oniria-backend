from django.urls import path
from .views import Communities,SimilarCommunities

urlpatterns = [
    path('', Communities.as_view(), name='communities'),
    path('<str:name>/',SimilarCommunities.as_view(),name="get-similar-communities")
]