from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AllPsychologists,
    SpecificPsychologist,
    AiTraining,
    AllForms,
    FormDetail,
    AllQuestions,
    QuestionDetail,
    CreateAnswer,
    AllFormResponse,
    AssignDueTests,
    SpecficDueTest,
    PsychologistApplicationViewSet 
)

# Router para ViewSets
router = DefaultRouter()
router.register(
    r'applications', 
    PsychologistApplicationViewSet, 
    basename='psychologist-application'
)

urlpatterns = [
    # ⚠️ IMPORTANTE: Rutas específicas PRIMERO, antes del router
    # Esto evita que el router capture 'psychologists' como un parámetro UUID
    
    # Rutas de Psicólogos
    path('psychologists/', AllPsychologists.as_view(), name='all_psychologists'),
    path('psychologists/<uuid:pk>/', SpecificPsychologist.as_view(), name='specific_psychologist'),
    
    # Rutas de Formularios
    path('forms/', AllForms.as_view(), name='all_forms'),
    path('forms/<uuid:pk>/', FormDetail.as_view(), name='form_detail'),
    
    # Rutas de Preguntas
    path('questions/', AllQuestions.as_view(), name='all_questions'),
    path('questions/<uuid:pk>/', QuestionDetail.as_view(), name='question_detail'),
    
    # Rutas de Respuestas
    path('answers/', CreateAnswer.as_view(), name='create_answer'),
    path('form-response/', AllFormResponse.as_view(), name='response-form'),
    
    # Rutas de Tests Asignados
    path('assign-due-tests/', AssignDueTests.as_view(), name='assign_due_tests'),
    path('due-tests/<uuid:pk>/', SpecficDueTest.as_view(), name='specific_due_test'),
    
    # Otras rutas
    path('ai-training/', AiTraining.as_view(), name='ai_training'),
    #path('upload-profile-pic/', UploadProfilePic.as_view(), name='upload_profile_pic'),
    
    # ⚠️ Router AL FINAL - esto permite que las rutas específicas tengan prioridad
    path('', include(router.urls)),
]