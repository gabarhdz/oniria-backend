from decouple import config
from dotenv import load_dotenv
from django.utils.deconstruct import deconstructible
import logging

logger = logging.getLogger(__name__)

@deconstructible
class deepseek_basic_call:
    def __call__(self, prompt,topic=None):
        try:
            load_dotenv()

            # Verificar que la API key existe
            api_key = config("DEEPSEEK_API_KEY", default="")
            if not api_key:
                logger.error("DEEPSEEK_API_KEY no está configurada")
                return "Error: La API key de DeepSeek no está configurada."

            try:
                from openai import OpenAI
            except ImportError:
                logger.error("La dependencia 'openai' no está instalada")
                return "Error: La dependencia 'openai' no está instalada."

            # Inicializar cliente OpenAI para DeepSeek
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/",
                timeout=30.0  # Timeout de 30 segundos
            )

            # Intentar conectar con ChromaDB
            

                # Combinar resultados
           

        # 6. Llamar a DeepSeek
            system_message = (
                "Evalua si el prompt proporcionado es apropiado y seguro para todo tipo de usuarios. "
                "Si el prompt es inapropiado, peligroso o viola las políticas, responde con 403. "
                "Si el prompt es apropiado, responde 200."
                " Responde solo con el código de estado sin explicaciones."
            )

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
                ],
                stream=False
            )

            # 7. Retornar respuesta
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error en deepseek_basic_call: {str(e)}")
            return f"Error en deepseek_basic_call: {str(e)}"
