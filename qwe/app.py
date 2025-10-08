from flask import Flask, render_template, request, jsonify
import random
import string

# Создаем экземпляр Flask приложения (ИСПРАВЛЕНО)
app = Flask(__name__)

def generate_password(length=12, use_uppercase=True, use_numbers=True, use_special=True):
    """
    Генерирует случайный пароль на основе заданных параметров.
    
    Args:
        length (int): Длина пароля (по умолчанию 12)
        use_uppercase (bool): Использовать заглавные буквы
        use_numbers (bool): Использовать цифры
        use_special (bool): Использовать специальные символы
    
    Returns:
        str: Сгенерированный пароль
    """
    # Начинаем с базового набора символов - строчные буквы
    characters = string.ascii_lowercase
    
    # Добавляем заглавные буквы, если выбрано
    if use_uppercase:
        characters += string.ascii_uppercase
    
    # Добавляем цифры, если выбрано
    if use_numbers:
        characters += string.digits
    
    # Добавляем специальные символы, если выбрано
    if use_special:
        characters += string.punctuation
    
    # Если никакие типы символов не выбраны, используем только строчные буквы
    if not characters:
        characters = string.ascii_lowercase
    
    # Генерируем пароль: выбираем случайные символы из набора characters
    # в количестве, равном length
    password = ''.join(random.choice(characters) for _ in range(length))
    
    return password

@app.route('/')
def index():
    """
    Обрабатывает главную страницу сайта.
    Возвращает HTML шаблон с формой для генерации пароля.
    """
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """
    Обрабатывает AJAX запросы на генерацию пароля.
    Принимает параметры из формы и возвращает JSON с паролем или ошибкой.
    """
    try:
        # Получаем данные из JSON запроса
        data = request.json
        
        # Извлекаем параметры с значениями по умолчанию
        length = int(data.get('length', 12))
        use_uppercase = data.get('uppercase', True)
        use_numbers = data.get('numbers', True)
        use_special = data.get('special', True)
        
        # Проверяем минимальную длину пароля
        if length < 4:
            return jsonify({
                'success': False,
                'error': 'Длина пароля должна быть не менее 4 символов'
            })
        
        # Проверяем максимальную длину пароля
        if length > 50:
            return jsonify({
                'success': False,
                'error': 'Длина пароля не должна превышать 50 символов'
            })
        
        # Генерируем пароль с заданными параметрами
        password = generate_password(length, use_uppercase, use_numbers, use_special)
        
        # Возвращаем успешный ответ с паролем
        return jsonify({
            'success': True,
            'password': password
        })
        
    except ValueError:
        # Обрабатываем ошибку неверного формата числа
        return jsonify({
            'success': False,
            'error': 'Неверный формат длины пароля'
        })
    except Exception as e:
        # Обрабатываем все остальные ошибки
        return jsonify({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })

def check_password_strength(password):
    """
    Проверяет сложность пароля и возвращает оценку.
    
    Args:
        password (str): Пароль для проверки
    
    Returns:
        dict: Результат проверки с оценкой и рекомендациями
    """
    score = 0
    feedback = []
    
    # Проверяем длину пароля
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
        feedback.append("Используйте пароль длиной не менее 12 символов")
    else:
        feedback.append("Пароль слишком короткий")
    
    # Проверяем наличие заглавных букв (ИСПРАВЛЕНО - убрали лишний комментарий)
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Добавьте заглавные буквы")
    
    # Проверяем наличие строчных букв
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Добавьте строчные буквы")
    
    # Проверяем наличие цифр
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Добавьте цифры")
    
    # Проверяем наличие специальных символов
    if any(c in string.punctuation for c in password):
        score += 1
    else:
        feedback.append("Добавьте специальные символы")
    
    # Определяем уровень сложности на основе набранных баллов
    if score >= 5:
        strength = "Очень сильный"
    elif score >= 4:
        strength = "Сильный"
    elif score >= 3:
        strength = "Средний"
    else:
        strength = "Слабый"
    
    return {
        'score': score,
        'strength': strength,
        'feedback': feedback
    }

@app.route('/generate-advanced', methods=['POST'])
def generate_advanced():
    """
    Расширенная версия генератора с проверкой сложности пароля.
    """
    try:
        data = request.json
        
        length = int(data.get('length', 12))
        use_uppercase = data.get('uppercase', True)
        use_numbers = data.get('numbers', True)
        use_special = data.get('special', True)
        
        # Проверяем валидность длины пароля
        if length < 4 or length > 50:
            return jsonify({
                'success': False,
                'error': 'Длина пароля должна быть от 4 до 50 символов'
            })
        
        # Генерируем пароль
        password = generate_password(length, use_uppercase, use_numbers, use_special)
        
        # Проверяем сложность пароля
        strength_analysis = check_password_strength(password)
        
        # Возвращаем расширенный ответ
        return jsonify({
            'success': True,
            'password': password,
            'strength': strength_analysis['strength'],
            'score': strength_analysis['score'],
            'feedback': strength_analysis['feedback']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
if __name__ == '__main__':
    app.run(debug=True)
