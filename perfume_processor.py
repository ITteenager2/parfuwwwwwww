import csv
import re
import os
from typing import List, Dict

def process_perfume_data() -> List[Dict[str, str]]:
    processed_data = []
    
    # Получаем путь к текущей директории скрипта
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Создаем полный путь к файлу CSV
    file_path = os.path.join(current_dir, 'edpby.csv')
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 3:
                url = row[2].strip('"')
                if url.startswith('https://edp.by/shop/') and '/' in url:
                    url_parts = url.split('/')
                    last_part = url_parts[-1]
                    if last_part and not last_part.startswith('page-') and '.' not in last_part:
                        name = re.sub(r'(\d+ml)', r' \1', last_part.replace('-', ' '))
                        formatted_name = ' '.join(word.capitalize() for word in name.split())
                        translated_name = formatted_name.replace('Parfyumernaya Voda', 'Парфюмерная вода')
                        processed_data.append({'url': url, 'name': translated_name})
    
    return processed_data

def get_perfume_recommendations(user_input: str, perfume_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    keywords = user_input.lower().split()
    recommendations = []
    
    for perfume in perfume_data:
        if any(keyword in perfume['name'].lower() for keyword in keywords):
            recommendations.append(perfume)
    
    return recommendations[:3]  # Return top-3 recommendations

# Загружаем данные при импорте модуля
perfume_data = process_perfume_data()