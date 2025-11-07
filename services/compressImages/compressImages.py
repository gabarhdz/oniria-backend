from django.utils.deconstruct import deconstructible
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import os

@deconstructible
class compressImages:
    def __init__(self, max_size=(1200, 1200), output_format='JPEG', quality=75):
        self.max_size = max_size
        self.output_format = output_format
        self.quality = quality

    def __call__(self, image_source):
        """
        image_source puede ser:
         - bytes / bytearray -> devuelve bytes procesados
         - file-like (con .read()) -> lee y procesa, devuelve bytes
         - ruta (str) existente -> procesa y sobrescribe el archivo (devuelve la ruta)
        """
        # Leer bytes desde distintos orígenes
        if isinstance(image_source, (bytes, bytearray)):
            data = bytes(image_source)
        elif hasattr(image_source, 'read'):
            try:
                image_source.seek(0)
            except Exception:
                pass
            data = image_source.read()
            try:
                image_source.seek(0)
            except Exception:
                pass
        elif isinstance(image_source, str) and os.path.exists(image_source):
            with open(image_source, 'rb') as f:
                data = f.read()
        else:
            raise TypeError("Unsupported image_source type for compressImages")

        # Procesar en memoria con Pillow
        buf_in = BytesIO(data)
        try:
            img = Image.open(buf_in)
            img.verify()  # valida encabezados
        except UnidentifiedImageError:
            raise
        except Exception as e:
            raise

        # Reabrir para transformar (verify() deja el objeto inutilizable)
        buf_in.seek(0)
        img = Image.open(buf_in).convert('RGB')
        img.thumbnail(self.max_size, Image.LANCZOS)

        out_buf = BytesIO()
        img.save(out_buf, format=self.output_format, quality=self.quality, optimize=True)
        out_buf.seek(0)
        processed_bytes = out_buf.read()

        # Si entró una ruta, sobrescribirla con los bytes JPEG procesados y devolver ruta
        if isinstance(image_source, str) and os.path.exists(image_source):
            with open(image_source, 'wb') as f:
                f.write(processed_bytes)
            return image_source

        # En caso de uploads en memoria, devolver bytes (imageHandler debería convertir a ContentFile)
        return processed_bytes