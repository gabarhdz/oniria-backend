# services/transformImageToBase64/transformImageToBase64.py
import base64
import filetype
from django.utils.deconstruct import deconstructible

@deconstructible
class transformImageToBase64:
    def __call__(self, image_path):
        """
        Convierte una imagen a base64 CON el prefijo data:image
        """
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            
        # Detectar el tipo de imagen
       # Detectar el tipo de imagen
        kind = filetype.guess(image_data)
        image_type = kind.extension if kind else 'jpeg'

        
        # Convertir a base64
        encoded_string = base64.b64encode(image_data).decode('utf-8')
        
        # Retornar CON prefijo data:image
        return f"data:image/{image_type};base64,{encoded_string}"