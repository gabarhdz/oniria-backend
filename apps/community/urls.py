from django.urls import path
from .views import Communities,SimilarCommunities,DetailedCommunity

urlpatterns = [
    path('<str:name>/',SimilarCommunities.as_view(),name="get-similar-communities"),
    path('specific/<str:pk>/', DetailedCommunity.as_view(),name='specific community'),
    path('', Communities.as_view(), name='communities')
    
]