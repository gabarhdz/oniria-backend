# services/imageHandler/imageHandler.py
from services.transformImageToBase64.transformImageToBase64 import TransformImageToBase64


class ImageHandler:
    @staticmethod
    def process_image(instance, uploaded_file):
        """
        Procesa una imagen cargada, la convierte a base64 y la guarda en el modelo.
        """
        try:
            # Guardar temporalmente la imagen
            temp_path = f"/tmp/{uploaded_file.name}"
            with open(temp_path, "wb") as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)

            # Convertir la imagen a base64
            base64_image = TransformImageToBase64.encode_image_to_base64(temp_path)

            # Guardar la imagen en el modelo
            instance.profile_pic_base64 = base64_image
            return base64_image
        except Exception as e:
            raise ValueError(f"Error al procesar la imagen: {e}")