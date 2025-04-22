import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt # type: ignore


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
    category = input("Category: ").strip().capitalize()
    date = input("Date (YYYY-MM-DD, Enter for today): ") or datetime.today().strftime('%Y-%m-%d')
    notes = input("Reminder (opt): ")

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (amount, category, date, notes) VALUES (?, ?, ?, ?)",
                   (amount, category, date, notes))
    conn.commit()
    conn.close()
    print("Expense added.")
    
# viewing all expenses

def view_expenses():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()

    print("\n--- All Expenses ---")
    for row in rows:
        print(f"{row[0]} | ${row[1]:.2f} | {row[2]} | {row[3]} | {row[4]}")


#Filtering by category and date

def filter_expenses():
    print("Leave a field blank to skip filtering it.")
    category = input("Filter by category: ").strip()
    date_input = input("Filter by date (DD-MM-YYYY): ").strip()

    date = None
    if date_input:
        try:
            # Convert to DB-friendly format
            date = datetime.strptime(date_input, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            print(" Invalid date format. Please use DD-MM-YYYY.")
            return

    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if category:
        query += " AND LOWER(category) = ?"
        params.append(category)
    if date:
        query += " AND date = ?"
        params.append(date)

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    print("\n--- Filtered Expenses ---")
    if not rows:
        print("No matching expenses found.")
    for row in rows:
        try:
            formatted_date = datetime.strptime(row[3], "%Y-%m-%d").strftime("%d-%m-%Y")
        except ValueError:
            formatted_date = row[3] 
        print(f"{row[0]} | ${row[1]:.2f} | {row[2]} | {formatted_date} | {row[4]}")
        
    # Spending summary
    
def show_summary():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0] or 0
    print(f"Total Spent: ${total:.2f}")

    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    print("Spending by Category:")
    for row in cursor.fetchall():
        print(f"{row[0]}: ${row[1]:.2f}")
    conn.close()
    
    # Add bar chart
    
def plot_bar_chart():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    conn.close()

    if not data:
        print(" No data to plot.")
        return

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.bar(categories, amounts)
    plt.xlabel('Category')
    plt.ylabel('Total ($)')
    plt.title('Spending by Category')
    plt.tight_layout()
    plt.show()
    
    # Add pie chart
    
def plot_pie_chart():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    conn.close()

    if not data:
        print(" No data to plot.")
        return

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.pie(amounts, labels=categories, autopct='%1.1f%%')
    plt.title('Spending Breakdown')
    plt.tight_layout()
    plt.show()
    
    # Add CSV export
    
import csv

def export_to_csv():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()

    with open('expenses_export.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Amount', 'Category', 'Date', 'Notes'])
        writer.writerows(rows)

    print("Exported to expenses_export.csv")
    
    

def main():
    init_db()
    while True:
        print("\n--- Expense Tracker Menu ---")
        print("1. Add Expense")
        print("2. View All")
        print("3. Filter Expenses")
        print("4. Show Summary")
        print("5. Bar Chart")
        print("6. Pie Chart")
        print("7. Export to CSV")
        print("8. Exit")

        choice = input("Choose (1–8): ")
        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            filter_expenses()
        elif choice == "4":
            show_summary()
        elif choice == "5":
            plot_bar_chart()
        elif choice == "6":
            plot_pie_chart()
        elif choice == "7":
            export_to_csv()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()

        
    
