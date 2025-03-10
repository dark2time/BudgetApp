import json
import os
from datetime import datetime, timedelta

CONFIG_FILE = "config.json"
DATA_FILE = "budget_data.json"
DEFAULT_CONFIG = {
    "daily_limit": 1000,
    "goals": {},
    "currency": "руб.",
    "theme": "darkly"
}


class BudgetManager:
    def __init__(self):
        self.data = {
            'incomes': {},
            'expenses': {},
            'limits': {},
            'last_reset': datetime.now().strftime('%Y-%m-%d'),
            'last_balance': 0
        }
        self.config = self.load_config()
        self.load_data()
        self.check_month_reset()

    # Конфигурация
    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return DEFAULT_CONFIG.copy()
        except Exception as e:
            print(f"Ошибка загрузки конфига: {e}")
            return DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения конфига: {e}")
            return False

    # Данные
    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                self.data = json.load(f)

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    # Логика бюджета
    def check_month_reset(self):
        now = datetime.now()
        last_reset = datetime.strptime(self.data['last_reset'], '%Y-%m-%d')

        if now.month != last_reset.month:
            self.distribute_month_end_balance()
            self.data['limits'] = {}
            self.data['last_reset'] = now.strftime('%Y-%m-%d')
            self.save_data()

    def get_current_balance(self):
        total_income = sum(float(amt) for amt in self.data['incomes'].values())
        total_expenses = sum(float(amt) for amt in self.data['expenses'].values())
        return total_income - total_expenses

    def add_income(self, date, amount):
        self.data['incomes'][date] = float(amount)
        self.process_income(float(amount))
        self.save_data()

    def add_expense(self, date, amount):
        amount = float(amount)
        if date != datetime.now().strftime('%Y-%m-%d'):
            return False
        allowed = self.get_daily_limit(date)
        if amount > allowed:
            return False
        self.data['expenses'][date] = self.data['expenses'].get(date, 0) + amount
        self.update_limits(date, amount)
        self.save_data()
        return True

    def get_daily_limit(self, date):
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        prev_day = (date_obj - timedelta(days=1)).strftime('%Y-%m-%d')

        if date in self.data['limits']:
            return float(self.data['limits'][date])

        if prev_day in self.data['limits']:
            remaining = float(self.data['limits'][prev_day]) - float(self.data['expenses'].get(prev_day, 0))
            return remaining + self.config['daily_limit']

        return self.config['daily_limit']

    def update_limits(self, date, spent):
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        next_day = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')
        remaining = self.get_daily_limit(date) - spent
        self.data['limits'][next_day] = remaining + self.config['daily_limit']
        self.save_data()

    def distribute_month_end_balance(self):
        balance = self.get_current_balance()
        if balance > 0 and self.config['goals']:
            total_percent = sum(self.config['goals'].values())
            if total_percent > 0:
                for goal, percent in self.config['goals'].items():
                    allocated = balance * percent / total_percent
                    self.data['incomes'][f"Цель: {goal}"] = self.data['incomes'].get(f"Цель: {goal}", 0) + allocated
                self.data['last_balance'] = balance
                self.save_data()

    def reset_data(self):
        self.data = {
            'incomes': {},
            'expenses': {},
            'limits': {},
            'last_reset': datetime.now().strftime('%Y-%m-%d'),
            'last_balance': 0
        }
        self.save_data()