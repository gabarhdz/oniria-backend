import base64
import mimetypes
from django.utils.deconstruct import deconstructible

@deconstructible
class transformImageToBase64:
    def __call__(self, image_path):
        # Detectar el tipo MIME del archivo
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            raise ValueError("No se pudo determinar el tipo MIME del archivo.")

        # Leer el archivo y convertirlo a base64
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        # Incluir el MIME al principio del string base64
        return f"data:{mime_type};base64,{encoded_string}"