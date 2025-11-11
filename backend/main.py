from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import mysql.connector

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
FRONTEND_DIR = ROOT_DIR / "frontend" 

@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "public" / "index.html")

app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name = "frontend")

DB_CONFIG ={
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "REMOVED_DB_PW",
    "database": "petshop"
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

# API 

# 型別設定
@app.get("/api/products")
def list_product(
    page: int = Query(1, ge=1),
    page_size: int = Query(3, ge=1, le=6),
    q: str | None = Query(None)
):

    # 設定篩選條件
    offset_data = (page - 1) * page_size
    condition = ["p.is_active = 1", "v.is_active = 1"]
    params: list = []

    if q:
        condition.append("p.name LIKE %s")
        params.append(f'%{q}%')

    where_sql = " AND ".join(condition)
    # 統計data總數
    count_sql = f'''
        SELECT COUNT(DISTINCT p.id) AS cnt FROM products p JOIN product_variants v
        ON p.id = v.product_id
        WHERE {where_sql}
    '''

    # 商品資料
    data_sql = f'''
    SELECT p.id, p.name, p.main_image, MIN(v.price) AS price_cents
    FROM products p JOIN product_variants v ON p.id = v.product_id
    WHERE {where_sql} GROUP BY p.id, p.name, p.main_image 
    ORDER BY p.id LIMIT %s OFFSET %s
    '''
    # 執行sql
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute(count_sql, params)
    total = cur.fetchone()["cnt"]

    cur.execute(data_sql, params + [page_size, offset_data])
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # 建立回傳json
    data = [{
        "id": r["id"],
        "name": r["name"],
        "img": r["main_image"],
        "price": r["price_cents"] // 100 if r["price_cents"] is not None else None}
        for r in rows]
    return {"data": data, "page": page, "page_size": page_size, "total": total}