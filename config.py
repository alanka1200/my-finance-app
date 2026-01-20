#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурационный файл для финансового трекера
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Токен бота Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN', '8023686337:AAHIWbshULZAdRNog2hQYEuYahapeM3WZw0')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'FinancialLead_bot')

# Настройки Web App
WEB_APP_URL = 'https://alanka1200.github.io/my-finance-app/'
WEB_APP_URL = os.getenv('WEB_APP_URL', 'https://alanka1200.github.io/my-finance-app/')
WEB_APP_PORT = int(os.getenv('WEB_APP_PORT', '8080'))

# Настройки приложения
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Финансовые настройки
DEFAULT_CURRENCY = '₽'
DEFAULT_LANGUAGE = 'ru'

# Пути к файлам
HTML_FILE_PATH = 'index.html'
DATA_FILE_PATH = 'user_data.json'

print(f"Конфигурация загружена: BOT_USERNAME={BOT_USERNAME}, WEB_APP_URL={WEB_APP_URL}")