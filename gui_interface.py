import tkinter as tk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from core_logic import BudgetManager
from datetime import datetime


class App(ttkb.Window):
    def __init__(self):
        self.budget = BudgetManager()
        super().__init__(themename=self.budget.config['theme'])
        self.title("Умный Бюджет")
        self.geometry("1000x700")
        self.create_widgets()
        self.update_display()

    def create_widgets(self):
        self.notebook = ttkb.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Вкладки
        self.tab_operations = ttkb.Frame(self.notebook)
        self.tab_goals = ttkb.Frame(self.notebook)
        self.tab_status = ttkb.Frame(self.notebook)

        self.notebook.add(self.tab_operations, text="Операции")
        self.notebook.add(self.tab_goals, text="Цели")
        self.notebook.add(self.tab_status, text="Статус")

        self.create_operations_tab()
        self.create_goals_tab()
        self.create_status_tab()

    def create_operations_tab(self):
        frame = ttkb.Frame(self.tab_operations)
        frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        btn_frame = ttkb.Frame(frame)
        btn_frame.pack(fill=X, pady=10)

        ttkb.Button(
            btn_frame,
            text="Добавить доход",
            command=self.add_income,
            bootstyle=SUCCESS
        ).pack(side=LEFT, padx=5)

        ttkb.Button(
            btn_frame,
            text="Добавить расход",
            command=self.add_expense,
            bootstyle=DANGER
        ).pack(side=LEFT, padx=5)

        self.tree = ttkb.Treeview(
            frame,
            columns=('Дата', 'Тип', 'Сумма', 'Описание'),
            show='headings',
            bootstyle=PRIMARY
        )

        self.tree.heading('Дата', text='Дата')
        self.tree.heading('Тип', text='Тип')
        self.tree.heading('Сумма', text=f"Сумма ({self.budget.config['currency']})")
        self.tree.heading('Описание', text='Описание')
        self.tree.pack(fill=BOTH, expand=True)

    def create_goals_tab(self):
        frame = ttkb.Frame(self.tab_goals)
        frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        btn_frame = ttkb.Frame(frame)
        btn_frame.pack(fill=X, pady=10)

        ttkb.Button(
            btn_frame,
            text="Добавить цель",
            command=self.add_goal,
            bootstyle=INFO
        ).pack(side=LEFT, padx=5)

        ttkb.Button(
            btn_frame,
            text="Удалить цель",
            command=self.remove_goal,
            bootstyle=WARNING
        ).pack(side=LEFT, padx=5)

        self.goals_tree = ttkb.Treeview(
            frame,
            columns=('Цель', 'Процент'),
            show='headings',
            bootstyle=SECONDARY
        )

        self.goals_tree.heading('Цель', text='Цель')
        self.goals_tree.heading('Процент', text='Процент (%)')
        self.goals_tree.pack(fill=BOTH, expand=True)

    def create_status_tab(self):
        frame = ttkb.Frame(self.tab_status)
        frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        self.lbl_balance = ttkb.Label(
            frame,
            text=f"Текущий баланс: 0.00 {self.budget.config['currency']}",
            font=('Helvetica', 14),
            bootstyle=INFO
        )
        self.lbl_balance.pack(pady=10)

        self.lbl_daily = ttkb.Label(
            frame,
            text=f"Доступно сегодня: {self.budget.config['daily_limit']} {self.budget.config['currency']}",
            font=('Helvetica', 12),
            bootstyle=PRIMARY
        )
        self.lbl_daily.pack(pady=5)

        self.lbl_goals = ttkb.Label(
            frame,
            text="Активные цели: Нет",
            font=('Helvetica', 12),
            bootstyle=SUCCESS
        )
        self.lbl_goals.pack(pady=5)

        ttkb.Button(
            frame,
            text="Настройки",
            command=self.open_settings,
            bootstyle=INFO
        ).pack(pady=10)

        ttkb.Button(
            frame,
            text="Сбросить все данные",
            command=self.reset_data,
            bootstyle=DANGER
        ).pack(pady=20)

    def update_display(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for date, amount in self.budget.data['incomes'].items():
            self.tree.insert('', 'end', values=(date, 'Доход', f"{amount:.2f}", ''))

        for date, amount in self.budget.data['expenses'].items():
            self.tree.insert('', 'end', values=(date, 'Расход', f"{amount:.2f}", ''))

        for i in self.goals_tree.get_children():
            self.goals_tree.delete(i)

        for goal, percent in self.budget.config['goals'].items():
            self.goals_tree.insert('', 'end', values=(goal, f"{percent}%"))

        balance = self.budget.get_current_balance()
        daily = self.budget.get_daily_limit(datetime.now().strftime('%Y-%m-%d'))
        goals = ", ".join(self.budget.config['goals'].keys()) or "Нет целей"

        self.lbl_balance.config(text=f"Текущий баланс: {balance:.2f} {self.budget.config['currency']}")
        self.lbl_daily.config(text=f"Доступно сегодня: {daily:.2f} {self.budget.config['currency']}")
        self.lbl_goals.config(text=f"Активные цели: {goals}")

    def add_income(self):
        dialog = IncomeDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self.budget.add_income(dialog.result['date'], dialog.result['amount'])
            self.update_display()

    def add_expense(self):
        dialog = ExpenseDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            success = self.budget.add_expense(dialog.result['date'], dialog.result['amount'])
            if not success:
                ttkb.dialogs.Messagebox.show_error(
                    f"Превышен дневной лимит! Доступно: {self.budget.get_daily_limit(datetime.now().strftime('%Y-%m-%d')):.2f}",
                    "Ошибка"
                )
            self.update_display()

    def add_goal(self):
        dialog = GoalDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            total = sum(self.budget.config['goals'].values()) + dialog.result['percent']
            if total > 100:
                ttkb.dialogs.Messagebox.show_error("Сумма процентов не может превышать 100%!", "Ошибка")
            else:
                self.budget.config['goals'][dialog.result['name']] = dialog.result['percent']
                self.budget.save_config()
                self.update_display()

    def remove_goal(self):
        selected = self.goals_tree.selection()
        if not selected:
            ttkb.dialogs.Messagebox.show_warning("Выберите цель для удаления", "Внимание")
            return

        goal = self.goals_tree.item(selected[0])['values'][0]
        if goal in self.budget.config['goals']:
            del self.budget.config['goals'][goal]
            self.budget.save_config()
            self.update_display()

    def open_settings(self):
        dialog = SettingsDialog(self, self.budget)
        self.wait_window(dialog)
        if self.budget.config['theme'] != self._style.theme.name:
            self.destroy()
            App().mainloop()

    def reset_data(self):
        if ttkb.dialogs.Messagebox.yesno("Вы уверены? Все финансовые данные будут удалены!", "Подтверждение"):
            self.budget.reset_data()
            self.update_display()


# Диалоговые окна
class IncomeDialog(ttkb.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Добавление дохода")
        self.result = None
        self.create_widgets()

    def create_widgets(self):
        ttkb.Label(self, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5)
        self.entry_date = ttkb.Entry(self)
        self.entry_date.grid(row=0, column=1, padx=5, pady=5)
        self.entry_date.insert(0, datetime.now().strftime('%Y-%m-%d'))

        ttkb.Label(self, text="Сумма:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_amount = ttkb.Entry(self)
        self.entry_amount.grid(row=1, column=1, padx=5, pady=5)

        ttkb.Button(self, text="Добавить", command=self.on_ok, bootstyle=SUCCESS).grid(row=2, columnspan=2, pady=10)

    def on_ok(self):
        try:
            self.result = {
                'date': self.entry_date.get(),
                'amount': float(self.entry_amount.get())
            }
            self.destroy()
        except:
            ttkb.dialogs.Messagebox.show_error("Некорректные данные", "Ошибка")


class ExpenseDialog(IncomeDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Добавление расхода")


class GoalDialog(ttkb.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Добавление цели")
        self.result = None
        self.create_widgets()

    def create_widgets(self):
        ttkb.Label(self, text="Название цели:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_name = ttkb.Entry(self)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        ttkb.Label(self, text="Процент (%):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_percent = ttkb.Entry(self)
        self.entry_percent.grid(row=1, column=1, padx=5, pady=5)

        ttkb.Button(self, text="Добавить", command=self.on_ok, bootstyle=INFO).grid(row=2, columnspan=2, pady=10)

    def on_ok(self):
        try:
            self.result = {
                'name': self.entry_name.get(),
                'percent': float(self.entry_percent.get())
            }
            self.destroy()
        except:
            ttkb.dialogs.Messagebox.show_error("Некорректные данные", "Ошибка")


class SettingsDialog(ttkb.Toplevel):
    def __init__(self, parent, budget):
        super().__init__(parent)
        self.title("Настройки")
        self.budget = budget
        self.result = None
        self.create_widgets()

    def create_widgets(self):
        ttkb.Label(self, text="Дневной лимит:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_limit = ttkb.Entry(self)
        self.entry_limit.grid(row=0, column=1, padx=5, pady=5)
        self.entry_limit.insert(0, str(self.budget.config['daily_limit']))

        ttkb.Label(self, text="Валюта:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_currency = ttkb.Entry(self)
        self.entry_currency.grid(row=1, column=1, padx=5, pady=5)
        self.entry_currency.insert(0, self.budget.config['currency'])

        ttkb.Label(self, text="Тема оформления:").grid(row=2, column=0, padx=5, pady=5)
        self.theme_combo = ttkb.Combobox(self, values=['darkly', 'litera', 'solar', 'superhero'])
        self.theme_combo.grid(row=2, column=1, padx=5, pady=5)
        self.theme_combo.set(self.budget.config['theme'])

        ttkb.Label(self, text="Цели (название: процент):").grid(row=3, column=0, padx=5, pady=5)
        self.goals_text = tk.Text(self, height=5, width=30)
        self.goals_text.grid(row=3, column=1, padx=5, pady=5)
        goals_str = "\n".join([f"{k}: {v}" for k, v in self.budget.config['goals'].items()])
        self.goals_text.insert('1.0', goals_str)

        btn_frame = ttkb.Frame(self)
        btn_frame.grid(row=4, columnspan=2, pady=10)

        ttkb.Button(
            btn_frame,
            text="Сохранить",
            command=self.on_save,
            bootstyle=SUCCESS
        ).pack(side=LEFT, padx=5)

        ttkb.Button(
            btn_frame,
            text="Отмена",
            command=self.destroy,
            bootstyle=DANGER
        ).pack(side=LEFT, padx=5)

    def on_save(self):
        try:
            new_config = {
                "daily_limit": float(self.entry_limit.get()),
                "currency": self.entry_currency.get(),
                "theme": self.theme_combo.get(),
                "goals": {}
            }

            # Парсинг целей
            goals = self.goals_text.get('1.0', 'end').strip().split('\n')
            for line in goals:
                if ':' in line:
                    name, percent = line.split(':', 1)
                    new_config['goals'][name.strip()] = float(percent.strip())

            self.budget.config = new_config
            if self.budget.save_config():
                self.destroy()
                ttkb.dialogs.Messagebox.show_info(
                    "Настройки сохранены!\nПерезапустите программу для применения темы.",
                    "Успех"
                )
            else:
                ttkb.dialogs.Messagebox.show_error("Ошибка сохранения настроек!", "Ошибка")

        except ValueError:
            ttkb.dialogs.Messagebox.show_error("Некорректные данные в полях!", "Ошибка")


if __name__ == "__main__":
    app = App()
    app.mainloop()