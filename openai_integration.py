from openai import AsyncOpenAI
from config import OPENAI_API_KEY

aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)



def get_prompt():
    try:
        with open('prompt.txt', 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading prompt file: {e}")

async def generate_perfume_recommendation(user_input):
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": get_prompt()},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "Извините, в данный момент сервис недоступен. Пожалуйста, попробуйте позже."
    except Exception as e:
        print(f"Unexpected error in OpenAI API call: {e}")
        return "Произошла неожиданная ошибка. Пожалуйста, попробуйте позже."



