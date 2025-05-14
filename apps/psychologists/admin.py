from django.contrib import admin
from .models import emotion, university, psychologist   

# Register your models here.
admin.site.register(emotion)
admin.site.register(university)
admin.site.register(psychologist)