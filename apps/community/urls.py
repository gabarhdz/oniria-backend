from django.urls import path
from .views import Communities,SimilarCommunities,DetailedCommunity,Posts,SpecPost,FilterPostByCommunity

urlpatterns = [
    path('post/',Posts.as_view(),name = "posts-view"),
    path('post/<str:pk>/',SpecPost.as_view(),name="spcific posts"),
    path('<str:name>/',SimilarCommunities.as_view(),name="get-similar-communities"),
    path('specific/<str:pk>/', DetailedCommunity.as_view(),name='specific community'),
    path('post/community/<str:community>/' ,FilterPostByCommunity.as_view(),name='filter-posts-by-community'),
    path('', Communities.as_view(), name='communities'),
    
    
]