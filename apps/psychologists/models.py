from django.db import models
from django.conf import settings  # Importamos settings para usar AUTH_USER_MODEL
from services.imageHandler.imageHandler import ImageHandler
import uuid
from django.db.models import Sum
import random

# Create your models here.
class emotion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=False, max_length=100)

class university(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=False, max_length=100)

    def __str__(self):
        return self.name

class psychologist(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Usamos settings.AUTH_USER_MODEL en lugar de 'auth.User'
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='psychologist_profile',
        related_query_name='psychologist_profiles'
    )
    university = models.ForeignKey(university, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True, max_length=15000)
    startDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class questions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    psychologist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question_text = models.TextField(null=False, max_length=1000)
    min_value = models.IntegerField(null=False, default=0)
    max_value = models.IntegerField(null=False, default=10)

    def __str__(self):
        return f"Question  {self.question_text[:50]}"

class forms(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    psychologist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(null=False, max_length=200)
    description = models.TextField(null=True, blank=True, max_length=5000)
    questions = models.ManyToManyField(questions, related_name='forms')  # Cambiado a ManyToManyField

    def __str__(self):
        return f"Form: {self.title} by {self.psychologist.username}"

class form_response(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(forms, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='form_responses')  # Usamos settings.AUTH_USER_MODEL
    created_at = models.DateTimeField(auto_now_add=True)
    total_score = models.IntegerField(null=True, blank=True, help_text="Suma de los valores de las answers")
    due_test = models.OneToOneField('DueTests', on_delete=models.SET_NULL, null=True, blank=True, related_name='form_response')
    def compute_total(self):
        """
        Calcula y actualiza el puntaje total basado en las respuestas asociadas.
        """
        agg = self.answers.aggregate(total=Sum('value'))
        total = agg['total'] or 0
        self.total_score = total
        self.save(update_fields=['total_score'])
        return total

    def __str__(self):
        return f"Response by {self.user.username} for {self.form.title} ({self.created_at.isoformat()})"

class answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    response = models.ForeignKey(form_response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(questions, on_delete=models.CASCADE)
    value = models.IntegerField()

    class Meta:
        unique_together = ('response', 'question')

    def __str__(self):
        return f"Answer to '{self.question.question_text[:40]}' = {self.value} (by {self.response.user.username})"

class PsychologistProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE
    )
    profile_pic_base64 = models.TextField(blank=True, null=True)  # Campo para guardar la imagen en base64

    def save_profile_pic(self, uploaded_file):
        """
        Procesa y guarda la imagen de perfil en base64.
        """
        handler = ImageHandler()
        self.profile_pic_base64 = handler.process_image(self, uploaded_file)
        self.save()


class DueTests(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    psychologist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='due_tests_psychologists',
        on_delete=models.CASCADE
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='due_tests_patients',
        on_delete=models.CASCADE
    )
    form = models.ForeignKey(
        forms,
        on_delete=models.CASCADE,
        related_name='due_test',
        null=True,
        blank=True
    )
    date = models.DateTimeField(null=False)
    description = models.TextField(null=True, blank=True, max_length=5000)
    is_completed = models.BooleanField(default=False)
    access_code = models.IntegerField(null=False, unique=True)

    def save(self, *args, **kwargs):
        """
        Generar un código de acceso único automáticamente si no se proporciona.
        """
        if not self.access_code:
            self.access_code = self.generate_unique_access_code()
        super().save(*args, **kwargs)

    def generate_unique_access_code(self):
        """
        Generar un código de acceso único de 6 dígitos.
        """
        while True:
            code = random.randint(100000, 999999)  
            if not DueTests.objects.filter(access_code=code).exists():
                return code

    def __str__(self):
        return f"DueTest for {self.patient.username} by {self.psychologist.username} on {self.date.isoformat()}"