from openai import OpenAI
import chromadb
from decouple import config
from dotenv import load_dotenv
from django.utils.deconstruct import deconstructible


@deconstructible
class deepseek_basic_call:
    def __call__(self, prompt):
       
        load_dotenv()

    
        client = OpenAI(
            api_key=config("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/"
        )

        chroma_client = chromadb.Client()
        collection = chroma_client.get_or_create_collection(name="noctiria-knowledge")

        # Search contexts in chroma
        query_results = collection.query(
            query_texts=[prompt],
            n_results=3  
        )

        # 4. Combinar los resultados en un solo bloque de texto
        if query_results["documents"]:
            context = "\n".join(query_results["documents"][0])
        else:
            context = "No se encontraron documentos relevantes."

        full_prompt = f"""
            Usa el siguiente contexto para responder la pregunta.

            Contexto:
            {context}

            Pregunta:
            {prompt}
            """

        # 6. Llamar a DeepSeek
        system_message = (
            "Eres un asistente experto en análisis de documentos enfocado en psicología, "
            "solamente responde preguntas de ese área. "
            "En caso de recibir una pregunta que no tiene que ver con psicología o sentimientos dirás lo siguiente: "
            "'Lo que has consultado va más allá de mi enfoque, mantengámonos en la línea de la psicología y emociones'. "
            "Usas lenguaje normal y sencillo y te esmeras en explicar y dejar todo muy claro y entendible."
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
