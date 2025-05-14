import os
from django.db.models.signals import post_delete,post_save
from django.dispatch import receiver
from apps.psychologists.models import psychologist
from .models import User

@receiver(post_delete, sender=User)
def delete_profile_pic_and_folders(sender, instance, **kwargs):
    if instance.profile_pic and instance.profile_pic.path:
        image_path = instance.profile_pic.path
        first_dir = os.path.dirname(image_path)           # user123/
        second_dir = os.path.dirname(first_dir)           # accounts/

        # Borrar imagen
        if os.path.isfile(image_path):
            os.remove(image_path)

        # Borrar carpeta user123/ si está vacía
        if os.path.isdir(first_dir) and not os.listdir(first_dir):
            os.rmdir(first_dir)

        # Borrar carpeta accounts/ si está vacía
        if os.path.isdir(second_dir) and not os.listdir(second_dir):
            os.rmdir(second_dir)
