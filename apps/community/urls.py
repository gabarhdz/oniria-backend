from django.urls import path
from .views import Communities,SimilarCommunities,DetailedCommunity,Posts,SpecPost,FilterPostByCommunity,GiveLikes, GiveDislikes,JoinCommunities

urlpatterns = [
    path('post/',Posts.as_view(),name = "posts-view"),
    path('post/<str:pk>/',SpecPost.as_view(),name="spcific posts"),
    path('<str:name>/',SimilarCommunities.as_view(),name="get-similar-communities"),
    path('specific/<str:pk>/', DetailedCommunity.as_view(),name='specific community'),
    path('post/community/<str:community>/' ,FilterPostByCommunity.as_view(),name='filter-posts-by-community'),
    path('post/like/<str:pk>/',GiveLikes.as_view(),name='give-like-to-a-post'),
    path('post/dislike/<str:pk>/',GiveDislikes.as_view(),name='give-dislike-to-a-post'),
    path('', Communities.as_view(), name='communities'),
    path('join/<str:pk>',JoinCommunities.as_view(),name="join-communites")
    
    
]