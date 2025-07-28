import os
from django.utils.deconstruct import deconstructible

@deconstructible
class UploadProfilePic:
    def __init__(self, base_dir='accounts'):
        self.base_dir = base_dir

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        path = os.path.join(
            self.base_dir,
            str(instance.id),
            'images',
            'profilepic'
        )
        return os.path.join(path, f'profilepic_of_{instance.id}.{ext}')
