#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер данных для финансового трекера
Вместо базы данных используем хранение в памяти
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class DataManager:
    """Класс для управления данными пользователей в памяти"""
    
    def __init__(self):
        self.users_data = {}
        self.transactions = {}
        self.goals = {}
        self.investments = {}
        
        # Загружаем тестовые данные
        self._load_initial_data()
    
    def _load_initial_data(self):
        """Загрузка начальных тестовых данных"""
        # Тестовый пользователь
        test_user_id = 123456
        self.users_data[test_user_id] = {
            'user_id': test_user_id,
            'username': 'ivan_dmitrienko',
            'first_name': 'Иван',
            'join_date': '2024-01-15',
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
        
        # Тестовые транзакции
        self.transactions[test_user_id] = [
            {
                'id': 1,
                'type': 'income',
                'category': 'зарплата',
                'amount': 120000,
                'description': 'Зарплата за январь',
                'date': '31.01.2024, 10:00'
            },
            {
                'id': 2,
                'type': 'expense',
                'category': 'еда',
                'amount': 25000,
                'description': 'Продукты на неделю',
                'date': '01.02.2024, 18:30'
            },
            {
                'id': 3,
                'type': 'expense',
                'category': 'транспорт',
                'amount': 5000,
                'description': 'Бензин',
                'date': '02.02.2024, 14:15'
            }
        ]
        
        # Тестовые цели
        self.goals[test_user_id] = [
            {
                'id': 1,
                'name': 'Новый ноутбук',
                'category': 'техника',
                'current': 25000,
                'target': 100000,
                'progress': 25.0,
                'days_left': 90,
                'deadline': '2024-06-30',
                'daily': 833.33,
                'created': '2024-01-15'
            },
            {
                'id': 2,
                'name': 'Путешествие в Турцию',
                'category': 'путешествие',
                'current': 33333,
                'target': 100000,
                'progress': 33.3,
                'days_left': 135,
                'deadline': '2024-08-15',
                'daily': 740.74,
                'created': '2024-01-20'
            }
        ]
        
        # Тестовые инвестиции
        self.investments[test_user_id] = [
            {
                'id': 1,
                'name': 'ЛУКОЙЛ',
                'type': 'Акции',
                'amount': 55000,
                'count': '10 шт.',
                'invested': 50000,
                'profit': 5000,
                'profit_percent': 10.0,
                'buy_date': '2024-01-15'
            },
            {
                'id': 2,
                'name': 'Bitcoin',
                'type': 'Криптовалюта',
                'amount': 25000,
                'count': '0.0005 шт.',
                'invested': 20000,
                'profit': 5000,
                'profit_percent': 25.0,
                'buy_date': '2024-02-01'
            },
            {
                'id': 3,
                'name': 'Сбербанк',
                'type': 'Акции',
                'amount': 32000,
                'count': '15 шт.',
                'invested': 30000,
                'profit': 2000,
                'profit_percent': 6.7,
                'buy_date': '2024-01-20'
            }
        ]
    
    # ========== МЕТОДЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ==========
    
    def get_user_data(self, user_id: int) -> Optional[Dict]:
        """Получение данных пользователя"""
        return self.users_data.get(user_id)
    
    def save_user_data(self, user_id: int, data: Dict) -> bool:
        """Сохранение данных пользователя"""
        self.users_data[user_id] = data
        return True
    
    def delete_user_data(self, user_id: int) -> bool:
        """Удаление данных пользователя"""
        if user_id in self.users_data:
            del self.users_data[user_id]
        if user_id in self.transactions:
            del self.transactions[user_id]
        if user_id in self.goals:
            del self.goals[user_id]
        if user_id in self.investments:
            del self.investments[user_id]
        return True
    
    # ========== МЕТОДЫ ДЛЯ ТРАНЗАКЦИЙ ==========
    
    def get_user_transactions(self, user_id: int) -> List[Dict]:
        """Получение транзакций пользователя"""
        return self.transactions.get(user_id, [])
    
    def add_transaction(self, user_id: int, transaction: Dict) -> bool:
        """Добавление новой транзакции"""
        if user_id not in self.transactions:
            self.transactions[user_id] = []
        
        # Генерируем ID если нет
        if 'id' not in transaction:
            transaction['id'] = int(datetime.now().timestamp() * 1000)
        
        self.transactions[user_id].append(transaction)
        return True
    
    def delete_transaction(self, user_id: int, transaction_id: Any) -> bool:
        """Удаление транзакции"""
        if user_id in self.transactions:
            self.transactions[user_id] = [
                t for t in self.transactions[user_id] 
                if str(t.get('id')) != str(transaction_id)
            ]
        return True
    
    # ========== МЕТОДЫ ДЛЯ ЦЕЛЕЙ ==========
    
    def get_user_goals(self, user_id: int) -> List[Dict]:
        """Получение целей пользователя"""
        return self.goals.get(user_id, [])
    
    def save_goal(self, user_id: int, goal: Dict) -> bool:
        """Сохранение цели"""
        if user_id not in self.goals:
            self.goals[user_id] = []
        
        # Проверяем, существует ли уже цель с таким ID
        for i, existing_goal in enumerate(self.goals[user_id]):
            if str(existing_goal.get('id')) == str(goal.get('id')):
                self.goals[user_id][i] = goal
                return True
        
        # Если цель новая, добавляем
        self.goals[user_id].append(goal)
        return True
    
    def delete_goal(self, user_id: int, goal_id: Any) -> bool:
        """Удаление цели"""
        if user_id in self.goals:
            self.goals[user_id] = [
                g for g in self.goals[user_id] 
                if str(g.get('id')) != str(goal_id)
            ]
        return True
    
    # ========== МЕТОДЫ ДЛЯ ИНВЕСТИЦИЙ ==========
    
    def get_user_investments(self, user_id: int) -> List[Dict]:
        """Получение инвестиций пользователя"""
        return self.investments.get(user_id, [])
    
    def save_investment(self, user_id: int, investment: Dict) -> bool:
        """Сохранение инвестиции"""
        if user_id not in self.investments:
            self.investments[user_id] = []
        
        # Проверяем, существует ли уже инвестиция с таким ID
        for i, existing_investment in enumerate(self.investments[user_id]):
            if str(existing_investment.get('id')) == str(investment.get('id')):
                self.investments[user_id][i] = investment
                return True
        
        # Если инвестиция новая, добавляем
        self.investments[user_id].append(investment)
        return True
    
    def delete_investment(self, user_id: int, investment_id: Any) -> bool:
        """Удаление инвестиции"""
        if user_id in self.investments:
            self.investments[user_id] = [
                inv for inv in self.investments[user_id] 
                if str(inv.get('id')) != str(investment_id)
            ]
        return True
    
    # ========== СЕРИАЛИЗАЦИЯ ДАННЫХ ==========
    
    def save_to_file(self, filepath: str) -> bool:
        """Сохранение всех данных в файл"""
        try:
            data = {
                'users': self.users_data,
                'transactions': self.transactions,
                'goals': self.goals,
                'investments': self.investments,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """Загрузка данных из файла"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.users_data = data.get('users', {})
                self.transactions = data.get('transactions', {})
                self.goals = data.get('goals', {})
                self.investments = data.get('investments', {})
                
                return True
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
        
        return False