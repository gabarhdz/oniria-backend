from django.urls import path
from .views import Communities,SimilarCommunities,DetailedCommunity,Posts,SpecPost

urlpatterns = [
    path('post/',Posts.as_view(),name = "posts-view"),
    path('post/<str:pk>/',SpecPost.as_view(),name="spcific posts"),
    path('<str:name>/',SimilarCommunities.as_view(),name="get-similar-communities"),
    path('specific/<str:pk>/', DetailedCommunity.as_view(),name='specific community'),
    path('', Communities.as_view(), name='communities'),
    
    
]