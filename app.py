#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web API для финансового трекера
Отдельный файл для Render без Telegram бота
"""

import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from data_manager import DataManager
from flask_cors import CORS

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация Flask
app = Flask(__name__)
CORS(app, origins=["https://alanka1200.github.io"])

# Менеджер данных
data_manager = DataManager()

# ========== API РОУТЫ (из вашего bot.py) ==========

@app.route('/api/user_data', methods=['GET'])
def get_user_data():
    """API: Получение данных пользователя"""
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    user_data = data_manager.get_user_data(user_id)
    
    if not user_data:
        # Возвращаем тестовые данные
        user_data = {
            'user_id': user_id,
            'first_name': 'Иван',
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
    
    # Добавляем транзакции, цели и инвестиции
    user_data['transactions'] = data_manager.get_user_transactions(user_id)
    user_data['goals'] = data_manager.get_user_goals(user_id)
    user_data['investments'] = data_manager.get_user_investments(user_id)
    
    return jsonify(user_data)

# Добавьте другие API-роуты из вашего bot.py сюда...
# (update_transaction, update_goal, update_investment, export_data и т.д.)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Finance Tracker API",
        "version": "1.0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)