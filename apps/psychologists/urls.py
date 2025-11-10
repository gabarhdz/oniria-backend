from django.urls import path
from .views import (
    AllPsychologists,
    SpecificPsychologist,
    AiTraining,
    AllForms,
    FormDetail,
    AllQuestions,
    CreateAnswer,
    current_psychologist_profile,
)




  
urlpatterns = [
    path('psychologists/', AllPsychologists.as_view(), name='all_psychologists'),
    path('psychologists/<int:pk>/', SpecificPsychologist.as_view(), name='specific_psychologist'),
    path('ai-training/', AiTraining.as_view(), name='ai_training'),
    path('forms/', AllForms.as_view(), name='all_forms'),
    path('forms/<int:pk>/', FormDetail.as_view(), name='form_detail'),
    path('questions/', AllQuestions.as_view(), name='all_questions'),
    path('answers/', CreateAnswer.as_view(), name='create_answer'),
    path('me/', current_psychologist_profile, name='current_psychologist'),

]
