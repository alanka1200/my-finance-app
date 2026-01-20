#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot + Web App для финансового трекера
Без базы данных - все в памяти
"""

import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from data_manager import DataManager
import config

from flask_cors import CORS

# Создаем приложение
app = Flask(__name__)

# Разрешаем запросы с вашего GitHub Pages
CORS(app, origins=["https://alanka1200.github.io"])

# Остальной код...

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация Flask для Web App
app = Flask(__name__)

# Инициализация бота
bot = telebot.TeleBot(config.BOT_TOKEN)

# Менеджер данных (вместо БД)
data_manager = DataManager()

# Словарь для хранения временных данных
temp_data = {}

# ========== КОМАНДЫ БОТА ==========

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Обработка команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    first_name = message.from_user.first_name or "Пользователь"
    
    # Регистрируем пользователя в системе
    user_data = data_manager.get_user_data(user_id)
    
    if not user_data:
        # Создаем нового пользователя
        user_data = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'join_date': datetime.now().strftime('%Y-%m-%d'),
            'balance': 25000,
            'monthly_income': 120000,
            'monthly_expenses': 95000,
            'savings_percent': 20.8,
            'investments_total': 25000,
            'financial_health': 75,
            'main_goal': 'Накопить на квартиру',
            'savings_goal': 50000,
            'investment_percent': 15
        }
        data_manager.save_user_data(user_id, user_data)
    
    # Создаем клавиатуру с кнопкой для открытия Web App
    keyboard = InlineKeyboardMarkup()
    web_app_button = InlineKeyboardButton(
        text="📊 Открыть финансовый трекер",
        web_app=WebAppInfo(url=f"{config.WEB_APP_URL}?user_id={user_id}")
    )
    keyboard.add(web_app_button)
    
    # Приветственное сообщение
    welcome_text = f"""
👋 Привет, {first_name}!

Добро пожаловать в **Финансовый Трекер** 🚀

Здесь ты сможешь:
• 📈 Отслеживать доходы и расходы
• 🎯 Ставить финансовые цели
• 📊 Анализировать свою статистику
• 💰 Управлять инвестициями
• 🧠 Получать персональные советы

Нажми кнопку ниже, чтобы открыть приложение 👇
"""
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.message_handler(commands=['help'])
def send_help(message):
    """Помощь по командам"""
    help_text = """
📚 Доступные команды:

/start - Начать работу с ботом
/help - Показать это сообщение
/stats - Получить краткую статистику
/reset - Сбросить данные (осторожно!)

💡 Просто нажми на кнопку "Открыть финансовый трекер" для полноценной работы с приложением!
"""
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def send_stats(message):
    """Отправка краткой статистики"""
    user_id = message.from_user.id
    user_data = data_manager.get_user_data(user_id)
    
    if user_data:
        stats_text = f"""
📊 Ваша финансовая статистика:

💰 Баланс: *{user_data['balance']:,} ₽*
📈 Доходы (месяц): *{user_data['monthly_income']:,} ₽*
📉 Расходы (месяц): *{user_data['monthly_expenses']:,} ₽*
💎 Сбережения: *{user_data['savings_percent']}%*
🏆 Финансовое здоровье: *{user_data['financial_health']}/100*

🎯 Главная цель: {user_data['main_goal']}
"""
    else:
        stats_text = "❌ Данные не найдены. Нажмите /start для начала работы."
    
    bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')

@bot.message_handler(commands=['reset'])
def reset_data(message):
    """Сброс данных пользователя"""
    user_id = message.from_user.id
    
    # Создаем клавиатуру подтверждения
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("✅ Да, сбросить", callback_data=f"reset_confirm_{user_id}"),
        InlineKeyboardButton("❌ Нет, отмена", callback_data=f"reset_cancel_{user_id}")
    )
    
    bot.send_message(
        message.chat.id,
        "⚠️ *Внимание!* Вы уверены, что хотите сбросить все ваши финансовые данные? Это действие нельзя отменить!",
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('reset_'))
def handle_reset(call):
    """Обработка сброса данных"""
    user_id = call.from_user.id
    action = call.data.split('_')[1]
    
    if action == 'confirm':
        data_manager.delete_user_data(user_id)
        bot.answer_callback_query(call.id, "✅ Данные успешно сброшены!")
        bot.send_message(call.message.chat.id, "🗑️ Все ваши данные были удалены. Нажмите /start для начала заново.")
    else:
        bot.answer_callback_query(call.id, "❌ Сброс отменен")
        bot.delete_message(call.message.chat.id, call.message.message_id)

# ========== FLASK API ДЛЯ WEB APP ==========

@app.route('/api/user_data', methods=['GET'])
def get_user_data():
    """API: Получение данных пользователя"""
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    user_data = data_manager.get_user_data(user_id)
    
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
    
    # Добавляем транзакции, цели и инвестиции
    user_data['transactions'] = data_manager.get_user_transactions(user_id)
    user_data['goals'] = data_manager.get_user_goals(user_id)
    user_data['investments'] = data_manager.get_user_investments(user_id)
    
    return jsonify(user_data)

@app.route('/api/update_transaction', methods=['POST'])
def update_transaction():
    """API: Добавление новой транзакции"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    transaction = {
        'id': datetime.now().timestamp(),
        'type': data.get('type', 'expense'),
        'category': data.get('category', 'other'),
        'amount': float(data.get('amount', 0)),
        'description': data.get('description', ''),
        'date': data.get('date', datetime.now().strftime('%d.%m.%Y, %H:%M'))
    }
    
    # Обновляем баланс пользователя
    user_data = data_manager.get_user_data(user_id)
    if user_data:
        if transaction['type'] == 'income':
            user_data['balance'] += transaction['amount']
            user_data['monthly_income'] += transaction['amount']
        else:
            user_data['balance'] -= transaction['amount']
            user_data['monthly_expenses'] += transaction['amount']
        
        # Пересчитываем проценты
        total = user_data['monthly_income'] + user_data['monthly_expenses']
        if total > 0:
            user_data['savings_percent'] = round(
                (user_data['monthly_income'] - user_data['monthly_expenses']) / user_data['monthly_income'] * 100, 
                1
            )
        
        data_manager.save_user_data(user_id, user_data)
    
    # Сохраняем транзакцию
    data_manager.add_transaction(user_id, transaction)
    
    return jsonify({'success': True, 'transaction': transaction})

@app.route('/api/update_goal', methods=['POST'])
def update_goal():
    """API: Добавление/обновление цели"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    goal = {
        'id': data.get('id', datetime.now().timestamp()),
        'name': data.get('name', 'Новая цель'),
        'category': data.get('category', 'other'),
        'current': float(data.get('current', 0)),
        'target': float(data.get('target', 10000)),
        'deadline': data.get('deadline', '2024-12-31'),
        'created': data.get('created', datetime.now().strftime('%Y-%m-%d'))
    }
    
    # Рассчитываем прогресс
    goal['progress'] = round((goal['current'] / goal['target']) * 100, 1) if goal['target'] > 0 else 0
    
    # Рассчитываем дни до дедлайна
    deadline_date = datetime.strptime(goal['deadline'], '%Y-%m-%d')
    days_left = (deadline_date - datetime.now()).days
    goal['days_left'] = max(days_left, 0)
    
    # Рассчитываем ежедневный взнос
    if goal['days_left'] > 0:
        goal['daily'] = round((goal['target'] - goal['current']) / goal['days_left'], 2)
    else:
        goal['daily'] = 0
    
    data_manager.save_goal(user_id, goal)
    
    return jsonify({'success': True, 'goal': goal})

@app.route('/api/update_investment', methods=['POST'])
def update_investment():
    """API: Добавление/обновление инвестиции"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    investment = {
        'id': data.get('id', datetime.now().timestamp()),
        'name': data.get('name', 'Новая инвестиция'),
        'type': data.get('type', 'Акции'),
        'amount': float(data.get('amount', 0)),
        'count': data.get('count', '1 шт.'),
        'invested': float(data.get('invested', 0)),
        'buy_date': data.get('buy_date', datetime.now().strftime('%Y-%m-%d'))
    }
    
    # Рассчитываем прибыль
    if investment['invested'] > 0:
        profit = investment['amount'] - investment['invested']
        profit_percent = round((profit / investment['invested']) * 100, 1)
        investment['profit'] = profit
        investment['profit_percent'] = profit_percent
    else:
        investment['profit'] = 0
        investment['profit_percent'] = 0
    
    data_manager.save_investment(user_id, investment)
    
    # Обновляем общую сумму инвестиций
    user_data = data_manager.get_user_data(user_id)
    if user_data:
        investments = data_manager.get_user_investments(user_id)
        total_investments = sum(inv['amount'] for inv in investments)
        user_data['investments_total'] = total_investments
        data_manager.save_user_data(user_id, user_data)
    
    return jsonify({'success': True, 'investment': investment})

@app.route('/api/delete_item', methods=['POST'])
def delete_item():
    """API: Удаление транзакции, цели или инвестиции"""
    data = request.json
    user_id = data.get('user_id')
    item_type = data.get('type')  # 'transaction', 'goal', 'investment'
    item_id = data.get('id')
    
    if not all([user_id, item_type, item_id]):
        return jsonify({'error': 'Missing parameters'}), 400
    
    if item_type == 'transaction':
        data_manager.delete_transaction(user_id, item_id)
    elif item_type == 'goal':
        data_manager.delete_goal(user_id, item_id)
    elif item_type == 'investment':
        data_manager.delete_investment(user_id, item_id)
    
    return jsonify({'success': True})

@app.route('/api/export_data', methods=['GET'])
def export_data():
    """API: Экспорт данных пользователя"""
    user_id = request.args.get('user_id', type=int)
    format_type = request.args.get('format', 'json')
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    # Получаем все данные пользователя
    user_data = data_manager.get_user_data(user_id)
    transactions = data_manager.get_user_transactions(user_id)
    goals = data_manager.get_user_goals(user_id)
    investments = data_manager.get_user_investments(user_id)
    
    export_data = {
        'user': user_data,
        'transactions': transactions,
        'goals': goals,
        'investments': investments,
        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if format_type == 'csv':
        # Простая CSV реализация
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Заголовок
        writer.writerow(['Финансовые данные пользователя', user_data.get('first_name', '')])
        writer.writerow(['Дата экспорта:', export_data['export_date']])
        writer.writerow([])
        
        # Общая информация
        writer.writerow(['ОБЩАЯ ИНФОРМАЦИЯ'])
        writer.writerow(['Баланс:', f"{user_data.get('balance', 0):,} ₽"])
        writer.writerow(['Доходы (месяц):', f"{user_data.get('monthly_income', 0):,} ₽"])
        writer.writerow(['Расходы (месяц):', f"{user_data.get('monthly_expenses', 0):,} ₽"])
        writer.writerow(['Сбережения:', f"{user_data.get('savings_percent', 0)}%"])
        writer.writerow(['Инвестиции:', f"{user_data.get('investments_total', 0):,} ₽"])
        writer.writerow([])
        
        # Транзакции
        writer.writerow(['ТРАНЗАКЦИИ'])
        writer.writerow(['Дата', 'Тип', 'Категория', 'Сумма', 'Описание'])
        for t in transactions:
            writer.writerow([
                t.get('date', ''),
                'Доход' if t.get('type') == 'income' else 'Расход',
                t.get('category', ''),
                f"{t.get('amount', 0):,} ₽",
                t.get('description', '')
            ])
        writer.writerow([])
        
        # Цели
        writer.writerow(['ФИНАНСОВЫЕ ЦЕЛИ'])
        writer.writerow(['Название', 'Категория', 'Текущее/Цель', 'Прогресс', 'Дедлайн'])
        for g in goals:
            writer.writerow([
                g.get('name', ''),
                g.get('category', ''),
                f"{g.get('current', 0):,} / {g.get('target', 0):,} ₽",
                f"{g.get('progress', 0)}%",
                g.get('deadline', '')
            ])
        writer.writerow([])
        
        # Инвестиции
        writer.writerow(['ИНВЕСТИЦИИ'])
        writer.writerow(['Название', 'Тип', 'Текущая стоимость', 'Инвестировано', 'Прибыль', 'Дата покупки'])
        for i in investments:
            writer.writerow([
                i.get('name', ''),
                i.get('type', ''),
                f"{i.get('amount', 0):,} ₽",
                f"{i.get('invested', 0):,} ₽",
                f"+{i.get('profit', 0):,} ₽ ({i.get('profit_percent', 0)}%)",
                i.get('buy_date', '')
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        response = app.response_class(
            response=csv_content,
            status=200,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=finance_data_{user_id}.csv'}
        )
        return response
    
    else:
        # JSON экспорт
        return jsonify(export_data)

@app.route('/api/get_referral_link', methods=['GET'])
def get_referral_link():
    """API: Получение реферальной ссылки"""
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    # Генерируем реферальную ссылку
    ref_link = f"https://t.me/{config.BOT_USERNAME}?start=ref_{user_id}"
    
    return jsonify({
        'success': True,
        'referral_link': ref_link,
        'message': 'Пригласите друга и получите скидку 10%!'
    })

# ========== ЗАПУСК СЕРВЕРА ==========

def run_flask():
    """Запуск Flask сервера"""
    app.run(
        host='0.0.0.0',
        port=config.WEB_APP_PORT,
        debug=config.DEBUG,
        use_reloader=False
    )

def run_bot():
    """Запуск Telegram бота"""
    logger.info("Запуск Telegram бота...")
    
    # Удаляем вебхук (если был)
    bot.remove_webhook()
    
    # Запускаем polling
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

if __name__ == '__main__':
    import threading
    
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Запускаем бота в основном потоке
    run_bot()