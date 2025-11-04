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
        1. Comprime la imagen.
        2. La guarda en un path temporal.
        3. La convierte a base64.
        4. Borra el archivo temporal.
        5. Devuelve la cadena base64.
        """
        # Crear un path temporal para guardar la imagen
        temp_path = self.temp_path_maker(instance, uploaded_file.name)

        # Guardar la imagen en el path temporal
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        with open(temp_path, 'wb') as temp_file:
            temp_file.write(uploaded_file.read())

        # Comprimir la imagen
        self.compressor(temp_path)

        # Convertir la imagen comprimida a base64
        base64_string = self.base64_encoder(temp_path)

        # Eliminar el archivo temporal
        os.remove(temp_path)

        return base64_string