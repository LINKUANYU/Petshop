import os
import mysql.connector
from fastapi import Depends, Request
from typing import Generator
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse

load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "petshop"),
}

def get_conn() -> Generator:
    """提供一條資料庫連線；生命週期交給 Depends 管，結束自動關閉。"""
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def get_cur(conn = Depends(get_conn)) -> Generator:
    """提供 dict 游標；結束自動關閉。"""
    cur = conn.cursor(dictionary=True)
    try:
        yield cur
    finally:
        cur.close()

def login_check(request: Request):
    """（預留）從 session 取得目前登入使用者 id。沒有登入回登入頁。"""
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    return user_id
