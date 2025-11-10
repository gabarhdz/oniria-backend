from django.contrib import admin
from .models import emotion, university, psychologist,questions, forms, form_response

# Register your models here.
admin.site.register(emotion)
admin.site.register(university)
admin.site.register(psychologist)
admin.site.register(questions)
admin.site.register(forms)
admin.site.register(form_response)