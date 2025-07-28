from django.utils.deconstruct import deconstructible
from PIL import Image
@deconstructible
class compressImages:
    def __call__(self, image_path):
        img = Image.open(image_path)
        img = img.convert('RGB')  
        img.save(image_path, format='JPEG', quality=45, optimize=True)

