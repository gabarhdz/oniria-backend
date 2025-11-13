from django.contrib import admin
from .models import emotion, university, psychologist,questions, forms, form_response, DueTests,answer, PsychologistApplication

# Register your models here.
admin.site.register(emotion)
admin.site.register(university)
admin.site.register(psychologist)
admin.site.register(questions)
admin.site.register(forms)
admin.site.register(form_response)
admin.site.register(DueTests)
admin.site.register(answer) 

@admin.register(PsychologistApplication)
class PsychologistApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'university_name',
        'status',
        'created_at',
        'reviewed_by'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email', 'university_name']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at']