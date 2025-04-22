import sqlite3
from datetime import datetime

# SQLite Database and expenses table

def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
# Func to input and save expenses

def add_expense():
    amount = float(input("Amount ($): "))
    category = input("Category: ")
    date = input("Date (YYYY-MM-DD, Enter for today): ") or datetime.today().strftime('%Y-%m-%d')
    notes = input("Reminder (opt): ")

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (amount, category, date, notes) VALUES (?, ?, ?, ?)",
                   (amount, category, date, notes))
    conn.commit()
    conn.close()
    print("Expense added.")

if __name__ == "__main__":
    init_db()
    add_expense()
