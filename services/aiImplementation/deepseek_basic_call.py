from openai import OpenAI
import chromadb
from decouple import config
from dotenv import load_dotenv
from django.utils.deconstruct import deconstructible
import logging

logger = logging.getLogger(__name__)

@deconstructible
class deepseek_basic_call:
    def __call__(self, prompt):
        try:
            load_dotenv()

            # Verificar que la API key existe
            api_key = config("DEEPSEEK_API_KEY", default="")
            if not api_key:
                logger.error("DEEPSEEK_API_KEY no está configurada")
                return "Error: La API key de DeepSeek no está configurada."

            # Inicializar cliente OpenAI para DeepSeek
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/",
                timeout=30.0  # Timeout de 30 segundos
            )

            # Intentar conectar con ChromaDB
            context = ""
            try:
                
                chromadb_api_key = config("CHROMADB_API_KEY", default="")
                
                if chromadb_api_key:
                    # ChromaDB Cloud
                    logger.info("Conectando a ChromaDB Cloud...")
                    chroma_client = chromadb.HttpClient(
                        host=config("CHROMADB_HOST", default="api.trychroma.com"),
                        port=443,
                        ssl=True,
                        headers={"x-chroma-token": chromadb_api_key},
                        tenant=config("CHROMADB_TENANT", default="default_tenant"),
                        database=config("CHROMADB_DATABASE", default="default_database"),
                    )
                else:
                    # ChromaDB Local
                    logger.info("Usando ChromaDB local...")
                    chroma_client = chromadb.Client()

                # Obtener o crear colección
                collection = chroma_client.get_or_create_collection(name="noctiria_knowledge")
                
                # Buscar contextos relevantes en ChromaDB
                query_results = collection.query(
                    query_texts=[prompt],
                    n_results=3
                )

                # Combinar resultados
                if query_results and query_results.get("documents") and query_results["documents"][0]:
                    context = "\n".join(query_results["documents"][0])
                    logger.info(f"Se encontraron {len(query_results['documents'][0])} documentos relevantes")
                else:
                    logger.warning("No se encontraron documentos relevantes en ChromaDB")
                    context = "No se encontraron documentos relevantes en la base de conocimiento."
                    
            except Exception as chroma_error:
                logger.warning(f"Error al conectar con ChromaDB: {str(chroma_error)}")
                context = "Base de conocimiento no disponible temporalmente."

            # Construir prompt completo
            if context and context != "Base de conocimiento no disponible temporalmente.":
                full_prompt = f"""Usa el siguiente contexto para responder la pregunta de manera clara y amigable.

            Contexto:
            {context}

            Pregunta:
            {prompt}

        Instrucciones:
        - Si el contexto es relevante, úsalo para dar una respuesta completa
        - Si el contexto no es relevante, responde basándote en tu conocimiento general
        - Usa un lenguaje sencillo y comprensible
        - Sé empático y profesional
        """
            else:
                full_prompt = f"""Responde la siguiente pregunta de manera clara, amigable y profesional:

        {prompt}

        Usa un lenguaje sencillo y comprensible."""

            # Llamar a DeepSeek
            logger.info("Enviando prompt a DeepSeek...")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres Noctiria AI, un asistente experto en psicología y análisis de sueños. Usas lenguaje normal y sencillo, eres empático y te esfuerzas en explicar todo de manera clara y entendible. Ayudas a las personas a comprender mejor sus sueños y su salud mental."
                    },
                    {
                        "role": "user", 
                        "content": full_prompt
                    },
                ],
                stream=False,
                temperature=0.7,
                max_tokens=1000
            )

            logger.info("Respuesta de DeepSeek recibida exitosamente")
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error en deepseek_basic_call: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return f"Lo siento, experimenté un error al procesar tu mensaje. Por favor, intenta nuevamente. (Error: {str(e)[:100]})"