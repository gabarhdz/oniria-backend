from django.contrib import admin
from .models import User
from unfold.admin import ModelAdmin as unfoldModelAdmin
# Register your models here.
admin.site.register(User)
class ModelAdmin(unfoldModelAdmin):
    pass