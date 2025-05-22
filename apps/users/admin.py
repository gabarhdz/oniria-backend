from django.contrib import admin
from .models import User,SleepState
from unfold.admin import ModelAdmin as unfoldModelAdmin
# Register your models here.
admin.site.register(User)
admin.site.register(SleepState)
class ModelAdmin(unfoldModelAdmin):
    pass