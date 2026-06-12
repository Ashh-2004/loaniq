import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="loaniq_db"
)

def fetch_all(query: str, params: tuple = ()) -> list:
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute(query, params)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def execute(query: str, params: tuple = ()) -> None:
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    cur.close()
    conn.close()