import re
import unicodedata
from transliterate import translit

def prepare_str_for_url(text): #AI created
    """
    Версия с использованием библиотеки transliterate.
    Пробелы заменяются на нижние подчеркивания.
    """
    if not text:
        return "untitled"
    
    # Транслитерируем русский текст
    try:
        text = translit(text, 'ru', reversed=True)
    except:
        pass  # Если текст не русский, оставляем как есть
    
    # Нормализуем и очищаем
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    
    # Шаг 1: Заменяем пробелы на нижние подчеркивания
    text = re.sub(r'\s+', '_', text)
    
    # Шаг 2: Заменяем другие разделители на дефисы
    text = re.sub(r'[\.,]+', '-', text)
    
    # Удаляем все недопустимые символы
    text = re.sub(r'[^a-z0-9_-]', '', text)
    
    # Удаляем множественные дефисы/подчеркивания
    text = re.sub(r'-+', '-', text)
    text = re.sub(r'_+', '_', text)
    text = text.strip('-_')
    
    return text
