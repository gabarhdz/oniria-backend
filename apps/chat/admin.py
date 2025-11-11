from django.contrib import admin
from .models import Conversation, Message, ChatNotification

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'psychologist', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'psychologist__username']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'conversation', 'created_at', 'is_read']
    list_filter = ['is_read', 'is_system_message', 'created_at']
    search_fields = ['content', 'sender__username']

@admin.register(ChatNotification)
class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient', 'conversation', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['recipient__username']