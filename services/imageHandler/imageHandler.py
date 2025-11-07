# services/imageHandler/imageHandler.py
import os
from ..compressImages.compressImages import compressImages
from ..makeTempPath.makeTempPath import makeTempPath
from ..transformImageToBase64.transformImageToBase64 import transformImageToBase64


class ImageHandler:
    def __init__(self, base_dir='tmp_uploads'):
        self.compressor = compressImages()
        self.temp_path_maker = makeTempPath(base_dir=base_dir)
        self.base64_encoder = transformImageToBase64()

    def process_image(self, instance, uploaded_file):
        """
        Procesa una imagen subida:
        1. Guarda en un path temporal.
        2. Comprime la imagen.
        3. La convierte a base64.
        4. Borra el archivo temporal.
        5. Devuelve la cadena base64.
        """
        # Crear un path temporal para guardar la imagen
        temp_path = self.temp_path_maker(instance, uploaded_file.name)

        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        # Guardar la imagen en el path temporal
        with open(temp_path, 'wb') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

        try:
            # Comprimir la imagen
            self.compressor(temp_path)

            # Convertir la imagen comprimida a base64
            base64_string = self.base64_encoder(temp_path)

            return base64_string
            
        finally:
            # Eliminar el archivo temporal (siempre se ejecuta)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Intentar eliminar directorios vacíos
            try:
                parent_dir = os.path.dirname(temp_path)
                if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
            except:
                pass