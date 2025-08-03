# services/UploadProfilePic/UploadProfilePic.py
import os
import uuid
from datetime import datetime

class UploadProfilePic:
    def __init__(self, base_dir='accounts'):
        self.base_dir = base_dir
    
    def __call__(self, instance, filename):
        """
        Genera una ruta única para el archivo de imagen de perfil
        """
        # Obtener la extensión del archivo
        ext = filename.split('.')[-1].lower()
        
        # Generar un nombre único usando UUID y timestamp
        unique_filename = f"{uuid.uuid4().hex}_{int(datetime.now().timestamp())}.{ext}"
        
        # Crear la ruta completa
        return os.path.join(self.base_dir, 'profile_pics', str(instance.id)[:2], unique_filename)
    
    @staticmethod
    def validate_image(image):
        """
        Valida que el archivo sea una imagen válida
        """
        from PIL import Image
        import io
        
        try:
            # Verificar que sea una imagen válida
            img = Image.open(image)
            img.verify()
            
            # Verificar el tamaño del archivo (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValueError("La imagen es demasiado grande. Máximo 5MB.")
            
            # Verificar formato
            allowed_formats = ['JPEG', 'PNG', 'GIF', 'WEBP']
            if img.format not in allowed_formats:
                raise ValueError(f"Formato no permitido. Use: {', '.join(allowed_formats)}")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Archivo de imagen inválido: {str(e)}")
    
    @staticmethod
    def resize_image(image, max_size=(800, 800)):
        """
        Redimensiona la imagen si es necesario
        """
        from PIL import Image
        import io
        from django.core.files.base import ContentFile
        
        try:
            img = Image.open(image)
            
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionar manteniendo proporción
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Guardar en memoria
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            # Crear nuevo archivo
            return ContentFile(output.read(), name=image.name)
            
        except Exception as e:
            raise ValueError(f"Error al procesar la imagen: {str(e)}")


# services/modelServices/generate_id.py (asegurándonos de que esté correcto)
import random
import string

def generate_id():
    """
    Genera un ID único de 20 caracteres
    """
    def generate():
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(20))
    
    return generate