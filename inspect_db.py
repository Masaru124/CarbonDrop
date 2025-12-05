import sqlite3

conn = sqlite3.connect('receipts.db')
cursor = conn.cursor()

print("Users:")
cursor.execute("SELECT id, username FROM users")
users = cursor.fetchall()
for u in users:
    print(u)

print("\nReceipts:")
cursor.execute("SELECT id, user_id, total_footprint, document_type, date FROM receipts")
receipts = cursor.fetchall()
for r in receipts:
    print(r)

print("\nItems:")
cursor.execute("SELECT id, receipt_id, name FROM items LIMIT 5")
items = cursor.fetchall()
for i in items:
    print(i)

conn.close()
