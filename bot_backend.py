import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ====================== НАСТРОЙКА ======================
TELEGRAM_BOT_TOKEN = "8023686337:AAHQM_-cVA2l5XPSyaEbGGo9PtvV2e5pVH0"  # Получите у @BotFather
WEB_APP_URL = "file:///C:/Users/Alan/Desktop/Fin_Tracker/finance_app.html"  # Или локальный ngrok URL

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====================== БАЗА ДАННЫХ В ПАМЯТИ ======================
users_data = {}
transactions_data = {}

# ====================== КЛАССЫ ДЛЯ ДАННЫХ ======================
class UserProfile:
    def __init__(self, user_id: int, username: str = "", full_name: str = ""):
        self.user_id = user_id
        self.username = username
        self.full_name = full_name
        self.registration_date = datetime.now()
        self.balance = 0.0
        self.monthly_budget = 0.0
        self.financial_goals = []
        self.categories = {
            'income': ['зарплата', 'подработка', 'инвестиции', 'подарки'],
            'expense': ['еда', 'транспорт', 'жилье', 'развлечения', 'образование', 'здоровье']
        }

class Transaction:
    def __init__(self, user_id: int, amount: float, category: str, transaction_type: str, description: str = ""):
        self.id = str(datetime.now().timestamp())
        self.user_id = user_id
        self.amount = amount
        self.category = category
        self.type = transaction_type  # 'income' или 'expense'
        self.description = description
        self.date = datetime.now()
        self.tags = []

# ====================== ФИНАНСОВЫЙ АНАЛИЗАТОР ======================
class FinancialAnalyzer:
    @staticmethod
    def calculate_monthly_summary(user_id: int) -> Dict:
        """Расчет месячной статистики"""
        if user_id not in transactions_data:
            return {"error": "Нет данных"}
        
        transactions = transactions_data[user_id]
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)
        
        monthly_transactions = [
            t for t in transactions 
            if t.date >= month_start
        ]
        
        if not monthly_transactions:
            return {"error": "Нет данных за месяц"}
        
        income = sum(t.amount for t in monthly_transactions if t.type == 'income')
        expense = sum(t.amount for t in monthly_transactions if t.type == 'expense')
        balance = income - expense
        
        # Структура расходов
        expense_by_category = {}
        for t in monthly_transactions:
            if t.type == 'expense':
                expense_by_category[t.category] = expense_by_category.get(t.category, 0) + t.amount
        
        # Проценты по категориям
        expense_percentages = {}
        if expense > 0:
            for category, amount in expense_by_category.items():
                expense_percentages[category] = round((amount / expense) * 100, 1)
        
        # Топ трат
        top_expenses = sorted(
            [t for t in monthly_transactions if t.type == 'expense'],
            key=lambda x: x.amount,
            reverse=True
        )[:5]
        
        return {
            "period": f"{month_start.strftime('%d.%m.%Y')} - {now.strftime('%d.%m.%Y')}",
            "income": round(income, 2),
            "expense": round(expense, 2),
            "balance": round(balance, 2),
            "transaction_count": len(monthly_transactions),
            "expense_structure": expense_percentages,
            "top_expenses": [
                {"category": t.category, "amount": t.amount, "date": t.date.strftime('%d.%m')}
                for t in top_expenses
            ]
        }
    
    @staticmethod
    def generate_financial_advice(summary: Dict) -> List[str]:
        """Генерация финансовых советов"""
        advice = []
        
        if "error" in summary:
            return ["Начните добавлять доходы и расходы для получения советов"]
        
        # Анализ баланса
        if summary["balance"] < 0:
            advice.append("⚠️ У вас отрицательный баланс! Рекомендуем сократить расходы.")
        
        # Анализ структуры расходов
        for category, percentage in summary["expense_structure"].items():
            if percentage > 30:
                advice.append(f"💰 На '{category}' уходит {percentage}% расходов. Проверьте, можно ли оптимизировать.")
        
        # Совет по накоплениям
        if summary["income"] > 0:
            save_ratio = (summary["balance"] / summary["income"]) * 100
            if save_ratio < 10:
                advice.append(f"💡 Вы откладываете {save_ratio:.1f}% дохода. Цель - 20% для финансовой стабильности.")
        
        # Положительные моменты
        if summary["balance"] > summary["income"] * 0.2:
            advice.append("✅ Отличный результат! Вы откладываете более 20% дохода.")
        
        if not advice:
            advice.append("📊 Ваши финансы в порядке. Продолжайте вести учёт!")
        
        return advice

# ====================== TELEGRAM BOT ======================
class FinanceBot:
    def __init__(self, token: str, web_app_url: str):
        self.token = token
        self.web_app_url = web_app_url
        self.analyzer = FinancialAnalyzer()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        
        # Создаем профиль пользователя, если его нет
        if user.id not in users_data:
            users_data[user.id] = UserProfile(user.id, user.username, user.full_name)
            transactions_data[user.id] = []
        
        # Создаем клавиатуру с кнопкой для Web App
        keyboard = [
            [InlineKeyboardButton(
                "📱 Открыть финансовый дашборд",
                web_app=WebAppInfo(url=self.web_app_url + f"?user_id={user.id}")
            )],
            [InlineKeyboardButton("➕ Добавить доход", callback_data="add_income")],
            [InlineKeyboardButton("➖ Добавить расход", callback_data="add_expense")],
            [InlineKeyboardButton("📊 Статистика", callback_data="get_stats")],
            [InlineKeyboardButton("💡 Советы", callback_data="get_advice")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            f"👋 Привет, {user.full_name}!\n\n"
            f"Я ваш персональный финансовый помощник.\n"
            f"Нажмите кнопку ниже, чтобы открыть интерактивный дашборд "
            f"или используйте команды для быстрых действий."
        )
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def handle_web_app_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка данных из Web App"""
        user_id = update.effective_user.id
        
        try:
            # Получаем данные от Web App
            data = json.loads(update.message.web_app_data.data)
            action = data.get("action")
            
            if action == "add_transaction":
                # Добавление транзакции из Web App
                amount = float(data["amount"])
                category = data["category"]
                trans_type = data["type"]
                description = data.get("description", "")
                
                transaction = Transaction(user_id, amount, category, trans_type, description)
                
                if user_id not in transactions_data:
                    transactions_data[user_id] = []
                transactions_data[user_id].append(transaction)
                
                # Обновляем баланс пользователя
                if user_id in users_data:
                    if trans_type == 'income':
                        users_data[user_id].balance += amount
                    else:
                        users_data[user_id].balance -= amount
                
                await update.message.reply_text(
                    f"✅ Транзакция добавлена!\n"
                    f"{'Доход' if trans_type == 'income' else 'Расход'}: {amount} ₽\n"
                    f"Категория: {category}"
                )
            
            elif action == "get_summary":
                # Получение статистики для Web App
                summary = self.analyzer.calculate_monthly_summary(user_id)
                advice = self.analyzer.generate_financial_advice(summary)
                
                response = {
                    "summary": summary,
                    "advice": advice
                }
                
                # Отправляем данные обратно через бота
                await update.message.reply_text(
                    f"📊 Ваша статистика:\n"
                    f"Доходы: {summary.get('income', 0)} ₽\n"
                    f"Расходы: {summary.get('expense', 0)} ₽\n"
                    f"Баланс: {summary.get('balance', 0)} ₽"
                )
        
        except Exception as e:
            logger.error(f"Ошибка обработки данных Web App: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке данных")
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий кнопок"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data == "add_income":
            await self.request_transaction(query, "income")
        elif query.data == "add_expense":
            await self.request_transaction(query, "expense")
        elif query.data == "get_stats":
            await self.send_statistics(query, user_id)
        elif query.data == "get_advice":
            await self.send_advice(query, user_id)
    
    async def request_transaction(self, query, trans_type: str):
        """Запрос транзакции"""
        categories = ["зарплата", "подработка", "инвестиции"] if trans_type == "income" else ["еда", "транспорт", "жилье", "развлечения"]
        categories_text = "\n".join([f"• {cat}" for cat in categories])
        
        text = (
            f"📝 Введите {trans_type} в формате:\n"
            f"<b>СУММА КАТЕГОРИЯ [описание]</b>\n\n"
            f"Пример: <code>15000 еда продукты на неделю</code>\n\n"
            f"Доступные категории:\n{categories_text}"
        )
        
        await query.edit_message_text(text=text, parse_mode='HTML')
        context.user_data['awaiting_transaction'] = trans_type
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстового ввода"""
        if 'awaiting_transaction' not in context.user_data:
            return
        
        trans_type = context.user_data.pop('awaiting_transaction')
        text = update.message.text.strip()
        parts = text.split(maxsplit=2)
        
        if len(parts) < 2:
            await update.message.reply_text("❌ Неверный формат. Используйте: СУММА КАТЕГОРИЯ [описание]")
            return      
        
        try:
            amount = float(parts[0])
            category = parts[1].lower()
            description = parts[2] if len(parts) > 2 else ""
            
            user_id = update.effective_user.id
            transaction = Transaction(user_id, amount, category, trans_type, description)
            
            if user_id not in transactions_data:
                transactions_data[user_id] = []
            transactions_data[user_id].append(transaction)
            
            # Обновляем баланс
            if user_id in users_data:
                if trans_type == 'income':
                    users_data[user_id].balance += amount
                else:
                    users_data[user_id].balance -= amount
            
            await update.message.reply_text(
                f"✅ {'Доход' if trans_type == 'income' else 'Расход'} добавлен!\n"
                f"Сумма: {amount} ₽\n"
                f"Категория: {category}\n"
                f"{f'Описание: {description}' if description else ''}"
            )
            
        except ValueError:
            await update.message.reply_text("❌ Сумма должна быть числом!")
    
    async def send_statistics(self, query, user_id: int):
        """Отправка статистики"""
        summary = self.analyzer.calculate_monthly_summary(user_id)
        
        if "error" in summary:
            await query.edit_message_text("📊 Нет данных для анализа. Добавьте несколько транзакций!")
            return
        
        stats_text = (
            f"📊 <b>Ваша финансовая статистика</b>\n\n"
            f"📅 Период: {summary['period']}\n"
            f"💰 Доходы: {summary['income']} ₽\n"
            f"💸 Расходы: {summary['expense']} ₽\n"
            f"📈 Баланс: {summary['balance']} ₽\n"
            f"📝 Операций: {summary['transaction_count']}\n\n"
        )
        
        if summary['expense_structure']:
            stats_text += "📋 Структура расходов:\n"
            for category, percentage in summary['expense_structure'].items():
                stats_text += f"• {category}: {percentage}%\n"
        
        await query.edit_message_text(stats_text, parse_mode='HTML')
    
    async def send_advice(self, query, user_id: int):
        """Отправка советов"""
        summary = self.analyzer.calculate_monthly_summary(user_id)
        advice_list = self.analyzer.generate_financial_advice(summary)
        
        advice_text = "💡 <b>Ваши персональные финансовые советы:</b>\n\n"
        for i, advice in enumerate(advice_list, 1):
            advice_text += f"{i}. {advice}\n"
        
        await query.edit_message_text(advice_text, parse_mode='HTML')
    
    def setup_handlers(self, application):
        """Настройка обработчиков"""
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.handle_web_app_data))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_input))
    
    async def run(self):
        """Запуск бота"""
        application = Application.builder().token(self.token).build()
        self.setup_handlers(application)
        
        await application.initialize()
        await application.start()
        logger.info("💰 Финансовый бот запущен!")
        
        # Запускаем polling
        await application.updater.start_polling()
        await asyncio.Event().wait()

# ====================== ЗАПУСК ======================
if __name__ == "__main__":
    bot = FinanceBot(TELEGRAM_BOT_TOKEN, WEB_APP_URL)
    
    print("=" * 60)
    print("💰 ФИНАНСОВЫЙ БОТ + WEB APP")
    print("=" * 60)
    print("1. Установите зависимости: pip install python-telegram-bot")
    print("2. Укажите токен бота и URL Web App")
    print("3. Запустите бот: python bot_backend.py")
    print("4. Запустите Web App: откройте finance_app.html в браузере")
    print("=" * 60)
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n✅ Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")