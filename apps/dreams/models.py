from django.db import models
from apps.users.models import User
from services.modelServices.generate_id import generate_id
from apps.psychologists.models import psychologist


# Create your models here.

#weak table of psychologist and exercise
# this table is used to store the exercises that a psychologist has assigned to a user
class psychologistExercise(models.Model):
    psychologist = models.ForeignKey(psychologist, on_delete=models.CASCADE)
    reason= models.TextField(max_length=500,blank=False,null=False)
    exercise = models.ForeignKey('exercise', on_delete=models.CASCADE)

    
class emotions(models.Model):
    name=models.CharField(max_length=80,blank=False,null=False)




class dream(models.Model):
    id=models.CharField(max_length=20, primary_key=True, default=generate_id, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=5000,blank=False,null=False)
    emotions =models.ManyToManyField(emotions)
    def save(self, *args, **kwargs):
        if not self.id:
            new_id = generate_id()
        # Ensure the ID is unique
            while dream.objects.filter(id=new_id).exists():
                new_id = generate_id()
            self.id = new_id
        super().save(*args, **kwargs)
    


class analisis(models.Model):
    psychologist = models.ForeignKey(psychologist,on_delete=models.CASCADE)
    dream = models.ForeignKey(dream,on_delete=models.CASCADE)
    analisis = models.TextField(max_length=450000,blank=False,null=False)

class exercise(models.Model):
    user = models.ManyToManyField(User)
    name = models.TextField(max_length=80,blank=False, null=False)
    description = models.TextField(max_length=900,blank=False,null=False)
    time = models.CharField(blank=False,null=False,max_length=80)
    psychologist = models.ManyToManyField(psychologist,through=psychologistExercise, blank=True)

    
