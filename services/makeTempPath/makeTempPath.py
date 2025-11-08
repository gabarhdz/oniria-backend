import os
import uuid
import base64
from datetime import datetime
from django.utils.deconstruct import deconstructible
from ..compressImages.compressImages import compressImages

@deconstructible
class makeTempPath:
    def __init__(self, base_dir='tmp_uploads'):
        self.base_dir = base_dir
    
    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        path = os.path.join(
            self.base_dir,
            str(instance.id),
            'images',
            'profilepic'
        )
        
        return os.path.join(path, f'{instance.id}.{ext}')