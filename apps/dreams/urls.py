from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AI_basic_call
from .emotional_views import (
    EmotionalEntryViewSet,
    EmotionalCategoryViewSet,
    EmotionalMilestoneViewSet,
    EmotionViewSet
)

router = DefaultRouter()
router.register(r'emotional-entries', EmotionalEntryViewSet, basename='emotional-entry')
router.register(r'emotional-categories', EmotionalCategoryViewSet, basename='emotional-category')
router.register(r'emotional-milestones', EmotionalMilestoneViewSet, basename='emotional-milestone')
router.register(r'emotions', EmotionViewSet, basename='emotion')

urlpatterns = [
    path('ai/basic/', AI_basic_call.as_view(), name='simple call to deepseek'),
    path('', include(router.urls)),
]
