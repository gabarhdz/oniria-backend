import base64
from django.utils.deconstruct import deconstructible

@deconstructible
class transformImageToBase64:
    def __call__(self, image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
