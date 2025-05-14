# utils.py
import random
import string
from django.utils.deconstruct import deconstructible

@deconstructible
class generate_id:
    def __call__(self, length=20):  # Hacerlo callable
        characters = string.ascii_lowercase + string.digits  # a-z + 0-9
        return ''.join(random.choices(characters, k=length))
