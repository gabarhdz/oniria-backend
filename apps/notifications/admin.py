from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'recipient',
        'sender',
        'notification_type',
        'title',
        'is_read',
        'created_at'
    ]
    list_filter = [
        'notification_type',
        'is_read',
        'created_at'
    ]
    search_fields = [
        'recipient__username',
        'sender__username',
        'title',
        'message'
    ]
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('recipient', 'sender', 'notification_type')
        }),
        ('Contenido', {
            'fields': ('title', 'message', 'redirect_url')
        }),
        ('Referencias', {
            'fields': ('community', 'post'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_read', 'created_at', 'read_at')
        }),
    )