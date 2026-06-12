import mysql.connector
import bcrypt
from faker import Faker
import random
from datetime import date, timedelta

fake = Faker('en_IN')
conn = mysql.connector.connect(host="localhost", user="root",
                                password="123456", database="loaniq_db")
cur = conn.cursor()

# Seed users (hashed passwords)
users = [
    ("admin",   "admin123",  "admin"),
    ("officer", "off123",    "officer"),
    ("viewer",  "view123",   "viewer"),
]
for u, p, r in users:
    hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
    cur.execute("INSERT INTO users (username, password_hash, role) VALUES (%s,%s,%s)",
                (u, hashed, r))

# Seed borrowers
for _ in range(50):
    cur.execute("""INSERT INTO borrowers
        (full_name, email, phone, credit_score, annual_income,
         employment_type, property_area, existing_loans, date_of_birth)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (
        fake.name(),
        fake.email(),
        fake.phone_number()[:15],
        random.randint(550, 850),
        random.randint(300000, 2000000),
        random.choice(['Salaried','Self-Employed','Business','Government']),
        random.choice(['Urban','Semi-Urban','Rural']),
        random.randint(0, 3),
        fake.date_of_birth(minimum_age=22, maximum_age=58)
    ))

conn.commit()
cur.close()
conn.close()
print("Seeded successfully.")