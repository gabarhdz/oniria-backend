from django.contrib import admin
from .models import psychologistExercise, emotions, dream, analisis, exercise
# Register your models here.
admin.site.register(psychologistExercise)
admin.site.register(emotions)
admin.site.register(dream)
admin.site.register(analisis)
admin.site.register(exercise)