from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from dialogue_manager import dialogue_manager
from perfume_processor import perfume_data, get_perfume_recommendations

aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)

def get_prompt():
    try:
        with open('prompt.txt', 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        return "You are an AI assistant specializing in perfume recommendations."

async def generate_perfume_recommendation(user_id, user_input):
    dialogue_history = dialogue_manager.get_dialogue_history(user_id)
    
    # Получаем рекомендации на основе пользовательского ввода
    recommendations = get_perfume_recommendations(user_input, perfume_data)
    
    # Форматируем рекомендации для включения в промпт
    formatted_recommendations = "\n".join([f"- {rec['name']} ({rec['url']})" for rec in recommendations])
    
    messages = [
        {"role": "system", "content": get_prompt()},
        *dialogue_history,
        {"role": "user", "content": user_input},
        {"role": "system", "content": f"Based on the user's input, here are some relevant perfume recommendations:\n{formatted_recommendations}\nPlease use this information to provide a personalized response."}
    ]

    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    recommendation = response.choices[0].message.content
    dialogue_manager.add_to_dialogue_history(user_id, "assistant", recommendation)
    return recommendation