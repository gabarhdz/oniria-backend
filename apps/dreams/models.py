from django.db import models
import uuid
from apps.users.models import User
from apps.psychologists.models import psychologist


# ==================== MODELOS EXISTENTES ====================

class psychologistExercise(models.Model):
    psychologist = models.ForeignKey(psychologist, on_delete=models.CASCADE)
    reason= models.TextField(max_length=500,blank=False,null=False)
    exercise = models.ForeignKey('exercise', on_delete=models.CASCADE)

    
class emotions(models.Model):
    name=models.CharField(max_length=80,blank=False,null=False)


class dream(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=5000,blank=False,null=False)
    emotions =models.ManyToManyField(emotions)
    

class analisis(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    psychologist = models.ForeignKey(psychologist,on_delete=models.CASCADE)
    dream = models.ForeignKey(dream,on_delete=models.CASCADE)
    analisis = models.TextField(max_length=450000,blank=False,null=False)


class exercise(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ManyToManyField(User)
    name = models.TextField(max_length=80,blank=False, null=False)
    description = models.TextField(max_length=900,blank=False,null=False)
    time = models.CharField(blank=False,null=False,max_length=80)
    psychologist = models.ManyToManyField(psychologist,through=psychologistExercise, blank=True)


# ==================== NUEVOS MODELOS PARA DIARIO EMOCIONAL ====================

class EmotionalCategory(models.Model):
    """
    Categorías para clasificar las entradas del diario emocional
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#9675bc')  # Color en formato hex
    icon = models.CharField(max_length=50, blank=True, null=True)  # Nombre del icono
    
    class Meta:
        verbose_name = 'Categoría Emocional'
        verbose_name_plural = 'Categorías Emocionales'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class EmotionalEntry(models.Model):
    """
    Entrada del diario emocional del usuario
    """
    MOOD_CHOICES = [
        ('very_bad', 'Muy Mal'),
        ('bad', 'Mal'),
        ('neutral', 'Neutral'),
        ('good', 'Bien'),
        ('very_good', 'Muy Bien'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emotional_entries')
    
    # Información básica
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=5000)
    entry_date = models.DateField()  # Fecha del evento emocional
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Estado emocional
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    intensity = models.IntegerField(default=5)  # Escala 1-10
    
    # Categorización
    categories = models.ManyToManyField(EmotionalCategory, related_name='entries', blank=True)
    emotions = models.ManyToManyField(emotions, related_name='emotional_entries', blank=True)
    
    # Tags personalizados
    tags = models.CharField(max_length=500, blank=True, null=True)  # Separados por comas
    
    # Análisis IA (opcional)
    ai_analysis = models.TextField(max_length=10000, blank=True, null=True)
    ai_analyzed_at = models.DateTimeField(blank=True, null=True)
    
    # Seguimiento
    is_private = models.BooleanField(default=True)
    is_favorite = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Entrada Emocional'
        verbose_name_plural = 'Entradas Emocionales'
        ordering = ['-entry_date', '-created_at']
        indexes = [
            models.Index(fields=['user', '-entry_date']),
            models.Index(fields=['user', 'mood']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.entry_date})"
    
    def get_tags_list(self):
        """Retorna lista de tags"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags_from_list(self, tags_list):
        """Establece tags desde una lista"""
        self.tags = ', '.join(tags_list)


class EmotionalMilestone(models.Model):
    """
    Hitos emocionales importantes del usuario
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emotional_milestones')
    entry = models.ForeignKey(
        EmotionalEntry, 
        on_delete=models.CASCADE, 
        related_name='milestone',
        blank=True,
        null=True
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    milestone_date = models.DateField()
    icon = models.CharField(max_length=50, default='star')
    color = models.CharField(max_length=7, default='#f1b3be')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Hito Emocional'
        verbose_name_plural = 'Hitos Emocionales'
        ordering = ['-milestone_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"