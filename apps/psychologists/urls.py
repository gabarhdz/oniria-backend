from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# Import después del router
from apps.psychologists import views

router.register(r'applications', views.PsychologistApplicationViewSet, basename='psychologist-application')

urlpatterns = [
    path('', include(router.urls)),
    path('psychologists/', views.AllPsychologists.as_view()),
    path('psychologist/profile/me/', views.current_psychologist_profile),
    path('psychologist/upload-profile-pic/', views.UploadProfilePic.as_view()),
    path('psychologist/<str:pk>/', views.SpecificPsychologist.as_view()),
    path('forms/', views.AllForms.as_view()),
    path('forms/<str:pk>/', views.FormDetail.as_view()),
    path('questions/', views.AllQuestions.as_view()),
    path('questions/<str:pk>/', views.QuestionDetail.as_view()),
    path('answers/', views.CreateAnswer.as_view()),
    path('form-response/', views.AllFormResponse.as_view()),
    path('assign-due-tests/', views.AssignDueTests.as_view()),
    path('due-tests/<str:pk>/', views.SpecficDueTest.as_view()),
    path('ai-training/', views.AiTraining.as_view()),
]