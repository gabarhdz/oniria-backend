import os
from django.utils.deconstruct import deconstructible

@deconstructible
class UploadProfilePic:
    def __init__(self, base_dir='accounts'):
        # Django guardará "base_dir='accounts'" en la migración
        self.base_dir = base_dir

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # No incluyas 'media/' aquí, Django lo antepondrá
        path = os.path.join(
            self.base_dir,
            str(instance.id),
            'images',
            'profilepic'
        )
        # Resultado: 'accounts/123/images/profilepic/profilepic_of_123.jpg'
        return os.path.join(path, f'profilepic_of_{instance.id}.{ext}')
