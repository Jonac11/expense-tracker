import sqlite3

conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()

# Get all distinct categories
cursor.execute("SELECT DISTINCT category FROM expenses")
categories = cursor.fetchall()

for cat in categories:
    original = cat[0]
    fixed = original.strip().capitalize()
    if original != fixed:
        print(f"Updating: '{original}' → '{fixed}'")
        cursor.execute("UPDATE expenses SET category = ? WHERE category = ?", (fixed, original))

conn.commit()
conn.close()
print(" Categories normalized.")
