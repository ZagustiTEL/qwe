from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import random
import string
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Замените на случайный ключ

# Настройка базы данных
DATABASE = 'users.db'

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    """Получение соединения с базой данных"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Инициализация базы данных при запуске
init_db()

# ==================== АВТОРИЗАЦИЯ ====================

def read_users():
    """Чтение пользователей из базы данных"""
    users = {}
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, password FROM users')
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        users[row['username']] = row['password']
    return users

def write_user(username, password):
    """Запись нового пользователя в базу данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, password)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # Пользователь уже существует
    finally:
        conn.close()
    return success

def user_exists(username):
    """Проверка существования пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def verify_password(username, password):
    """Проверка пароля"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return user['password'] == password
    return False

# ==================== ГЕНЕРАТОР ПАРОЛЕЙ ====================

def generate_password(length=12, use_uppercase=True, use_numbers=True, use_special=True):
    """
    Генерирует случайный пароль на основе заданных параметров.
    """
    characters = string.ascii_lowercase
    
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_numbers:
        characters += string.digits
    if use_special:
        characters += string.punctuation
    
    if not characters:
        characters = string.ascii_lowercase
    
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def check_password_strength(password):
    """
    Проверяет сложность пароля и возвращает оценку.
    """
    score = 0
    feedback = []
    
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
        feedback.append("Используйте пароль длиной не менее 12 символов")
    else:
        feedback.append("Пароль слишком короткий")
    
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Добавьте заглавные буквы")
    
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Добавьте строчные буквы")
    
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Добавьте цифры")
    
    if any(c in string.punctuation for c in password):
        score += 1
    else:
        feedback.append("Добавьте специальные символы")
    
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

# ==================== МАРШРУТЫ ====================

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if verify_password(username, password):
            session['username'] = username
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if not username or not password:
            flash('Заполните все поля', 'error')
        elif password != confirm_password:
            flash('Пароли не совпадают', 'error')
        elif user_exists(username):
            flash('Пользователь с таким именем уже существует', 'error')
        else:
            if write_user(username, password):
                flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Ошибка при регистрации пользователя', 'error')
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', username=session['username'])

@app.route('/password-generator')
def password_generator():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('index.html', username=session['username'])

@app.route('/generate', methods=['POST'])
def generate():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Требуется авторизация'})
    
    try:
        data = request.json
        
        length = int(data.get('length', 12))
        use_uppercase = data.get('uppercase', True)
        use_numbers = data.get('numbers', True)
        use_special = data.get('special', True)
        
        if length < 4:
            return jsonify({
                'success': False,
                'error': 'Длина пароля должна быть не менее 4 символов'
            })
        
        if length > 50:
            return jsonify({
                'success': False,
                'error': 'Длина пароля не должна превышать 50 символов'
            })
        
        password = generate_password(length, use_uppercase, use_numbers, use_special)
        
        return jsonify({
            'success': True,
            'password': password
        })
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Неверный формат длины пароля'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })

@app.route('/generate-advanced', methods=['POST'])
def generate_advanced():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Требуется авторизация'})
    
    try:
        data = request.json
        
        length = int(data.get('length', 12))
        use_uppercase = data.get('uppercase', True)
        use_numbers = data.get('numbers', True)
        use_special = data.get('special', True)
        
        if length < 4 or length > 50:
            return jsonify({
                'success': False,
                'error': 'Длина пароля должна быть от 4 до 50 символов'
            })
        
        password = generate_password(length, use_uppercase, use_numbers, use_special)
        strength_analysis = check_password_strength(password)
        
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

@app.route('/users')
def users():
    """Страница со списком пользователей"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    users_list = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT username, password FROM users ORDER BY username')
        rows = cursor.fetchall()
        conn.close()
        
        users_list = [{'username': row['username'], 'password': row['password']} for row in rows]
    except Exception as e:
        users_list = [{'username': f"Ошибка при чтении базы данных: {str(e)}", 'password': ''}]
    
    return render_template('users.html', users=users_list, username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)