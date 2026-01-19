# finance_bot.py
import logging
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext
from config import BOT_TOKEN, WEB_APP_URL

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Временное хранение данных в памяти (замени на БД позже)
users_data = {}
transactions_data = {}

async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Сохраняем базовую информацию
    if user_id not in users_data:
        users_data[user_id] = {
            'id': user_id,
            'name': user_name,
            'username': update.effective_user.username,
            'balance': 25000,
            'income': 120000,
            'joined': '2024-01-15'
        }
    
    keyboard = [
        [InlineKeyboardButton("📊 Открыть приложение", web_app={'url': WEB_APP_URL})],
        [InlineKeyboardButton("💰 Баланс", callback_data='balance'),
         InlineKeyboardButton("📈 Статистика", callback_data='stats')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Привет, {user_name}!\n"
        f"Добро пожаловать в FinGuide - твой персональный финансовый помощник!\n\n"
        f"🔹 Твой ID: {user_id}\n"
        f"🔹 Баланс: 25,000 ₽\n"
        f"🔹 Доход: 120,000 ₽\n\n"
        f"Нажми кнопку ниже чтобы открыть приложение ⬇️",
        reply_markup=reply_markup
    )

async def balance_command(update: Update, context: CallbackContext) -> None:
    """Команда для проверки баланса"""
    user_id = update.effective_user.id
    user_data = users_data.get(user_id, {})
    
    balance = user_data.get('balance', 25000)
    income = user_data.get('income', 120000)
    
    await update.callback_query.message.reply_text(
        f"💰 Твой финансовый обзор:\n\n"
        f"📊 Баланс: {balance:,} ₽\n"
        f"📈 Доход: {income:,} ₽\n"
        f"📉 Расходы: 95,000 ₽\n"
        f"💎 Сбережения: 20.8%\n\n"
        f"Открой приложение для детальной статистики!"
    )

def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    
    # Запуск бота
    print("🤖 Бот запущен! Нажмите Ctrl+C для остановки...")
    application.run_polling()

if __name__ == '__main__':
    main()
