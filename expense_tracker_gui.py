import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt  # type: ignore
import csv

# Database Setup
def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    # creates the table if it doesn't exist already
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

# Add Expense
def save_expense():
    try:
        amount = float(amount_entry.get())
        category = category_entry.get()
        date = date_entry.get() or datetime.today().strftime('%Y-%m-%d')
        notes = notes_entry.get()

        if not category:
            raise ValueError("Category is required.")  # quick check

        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (amount, category, date, notes) VALUES (?, ?, ?, ?)",
                       (amount, category, date, notes))
        conn.commit()
        conn.close()

        message_label.config(text="Expense added successfully.", fg="green")
        amount_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        notes_entry.delete(0, tk.END)

        print(f"Saved expense: ${amount} in {category} on {date}")  # debug log
        view_expenses()

    except ValueError:
        message_label.config(text="Please enter valid input.", fg="red")
        print("Invalid input for amount or missing category.")  # might improve later

# View All Expenses
def view_expenses():
    for row in expense_table.get_children():
        expense_table.delete(row)

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        expense_table.insert("", tk.END, values=row)

# Filter Expenses
def filter_expenses():
    for row in expense_table.get_children():
        expense_table.delete(row)

    category = filter_category_entry.get()
    date = filter_date_entry.get()

    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if date:
        query += " AND date = ?"
        params.append(date)

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        expense_table.insert("", tk.END, values=row)

# Summary
def show_summary():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0] or 0

    summary = f"Total Spent: ${total:.2f}\n\n"

    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    category_totals = cursor.fetchall()
    summary += "Spending by Category:\n"
    for row in category_totals:
        summary += f"{row[0]}: ${row[1]:.2f}\n"

    conn.close()
    messagebox.showinfo("Summary", summary)

# Charts
def plot_bar_chart():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    conn.close()

    if not data:
        messagebox.showinfo("Info", "No data to plot.")
        return

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.bar(categories, amounts)
    plt.xlabel('Category')
    plt.ylabel('Total Spent ($)')
    plt.title('Spending by Category')
    plt.tight_layout()
    plt.show()

def plot_pie_chart():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    conn.close()

    if not data:
        messagebox.showinfo("Info", "No data to plot.")
        return

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.pie(amounts, labels=categories, autopct='%1.1f%%')
    plt.title('Spending Breakdown')
    plt.tight_layout()
    plt.show()

# Export to CSV
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

    messagebox.showinfo("Export", "Data exported to expenses_export.csv")
    print("CSV export complete.")  # useful to know it worked

# GUI Layout
init_db()
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("800x700")

# Scrollable Canvas Setup
canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Input Form
tk.Label(scrollable_frame, text="Amount ($):").pack()
amount_entry = tk.Entry(scrollable_frame)
amount_entry.pack()

tk.Label(scrollable_frame, text="Category:").pack()
category_entry = tk.Entry(scrollable_frame)
category_entry.pack()

tk.Label(scrollable_frame, text="Date (YYYY-MM-DD):").pack()
date_entry = tk.Entry(scrollable_frame)
date_entry.pack()

tk.Label(scrollable_frame, text="Notes (optional):").pack()
notes_entry = tk.Entry(scrollable_frame)
notes_entry.pack()

tk.Button(scrollable_frame, text="Add Expense", command=save_expense).pack(pady=5)
message_label = tk.Label(scrollable_frame, text="")
message_label.pack()

# Filter Section
tk.Label(scrollable_frame, text="Filter by Category:").pack()
filter_category_entry = tk.Entry(scrollable_frame)
filter_category_entry.pack()

tk.Label(scrollable_frame, text="Filter by Date (YYYY-MM-DD):").pack()
filter_date_entry = tk.Entry(scrollable_frame)
filter_date_entry.pack()

tk.Button(scrollable_frame, text="Apply Filter", command=filter_expenses).pack(pady=5)
tk.Button(scrollable_frame, text="View All Expenses", command=view_expenses).pack(pady=5)

# Table Section
columns = ("ID", "Amount", "Category", "Date", "Notes")
expense_table = ttk.Treeview(scrollable_frame, columns=columns, show="headings", height=10)
for col in columns:
    expense_table.heading(col, text=col)
    expense_table.column(col, anchor=tk.CENTER)
expense_table.pack(fill=tk.BOTH, expand=True)

# Summary, Charts, Export
tk.Button(scrollable_frame, text="Show Spending Summary", command=show_summary).pack(pady=5)
tk.Button(scrollable_frame, text="Show Bar Chart", command=plot_bar_chart).pack(pady=5)
tk.Button(scrollable_frame, text="Show Pie Chart", command=plot_pie_chart).pack(pady=5)
tk.Button(scrollable_frame, text="Export to CSV", command=export_to_csv).pack(pady=5)

# Load data on start
view_expenses()
print("Expense tracker is running.")  # dev message
root.mainloop()
