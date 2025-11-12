import base64
import mimetypes

class TransformImageToBase64:
    @staticmethod
    def encode_image_to_base64(image_path):
        """
        Convierte una imagen en base64 con el prefijo adecuado para ser usada en React.
        """
        try:
            # Detectar el tipo MIME de la imagen
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                raise ValueError("No se pudo determinar el tipo MIME de la imagen.")

            # Leer la imagen en modo binario
            with open(image_path, "rb") as image_file:
                base64_data = base64.b64encode(image_file.read()).decode("utf-8")

            # Agregar el prefijo adecuado para React
            return f"data:{mime_type};base64,{base64_data}"
        except Exception as e:
            raise ValueError(f"Error al convertir la imagen a base64: {e}")

    @staticmethod
    def decode_base64_to_image(base64_string, output_path):
        """
        Decodifica una cadena base64 y guarda la imagen en el sistema de archivos.
        """
        try:
            # Separar el prefijo del contenido base64
            if base64_string.startswith("data:"):
                base64_data = base64_string.split(",")[1]
            else:
                base64_data = base64_string

            # Decodificar y guardar la imagen
            with open(output_path, "wb") as image_file:
                image_file.write(base64.b64decode(base64_data))
        except Exception as e:
            raise ValueError(f"Error al decodificar la imagen desde base64: {e}")
