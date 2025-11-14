from openai import OpenAI
import chromadb
from decouple import config
from dotenv import load_dotenv
from django.utils.deconstruct import deconstructible
import logging

logger = logging.getLogger(__name__)

@deconstructible
class deepseek_basic_call:
    def __call__(self, prompt,instructions=""):
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
                    
                    logger.info("Usando ChromaDB local...")
                    chroma_client = chromadb.Client()

                
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

            
            if context and context != "Base de conocimiento no disponible temporalmente.":
                full_prompt = f"""Usa el siguiente contexto para responder la pregunta de manera clara y amigable.

            Contexto:
            {context}

            Pregunta:
            {prompt}
            """

        # 6. Llamar a DeepSeek
            system_message = (
                instructions if instructions else "Eres un asistente útil y amigable que responde de manera clara y concisa. No responda información que no tenga que ver con el contexto de atención psicologica, responde con palabras sencillas, responde siempre los saludos"
            )

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": full_prompt},
                ],
                stream=False
            )

            # 7. Retornar respuesta
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error en deepseek_basic_call: {str(e)}")
            return f"Error en deepseek_basic_call: {str(e)}"
