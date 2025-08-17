# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI
from dotenv import load_dotenv
from decouple import config
#set dotenv


@deconstructible
class deepseek_basic_call:
    def __call__(self, prompt):
        load_dotenv()

        client = OpenAI(api_key=config('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )

        return response.choices[0].message.content