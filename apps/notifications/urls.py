from django.urls import path
from .views import (
    NotificationListView,
    NotificationDetailView,
    NotificationMarkAllReadView,
    NotificationUnreadCountView,
    NotificationClearAllView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<str:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
    path('clear-all/', NotificationClearAllView.as_view(), name='notification-clear-all'),
]