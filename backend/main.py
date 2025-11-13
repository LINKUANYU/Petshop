from pathlib import Path
from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import mysql.connector

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
FRONTEND_DIR = ROOT_DIR / "frontend" 
BACKEND_STATIC = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/daily_discover")
def home(request: Request):
    return templates.TemplateResponse("daily.html", {"request": request})


app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name = "frontend")
app.mount("/static", StaticFiles(directory=BACKEND_STATIC), name = "backend-static")

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

PAGE_SIZE = 5

# 型別設定
@app.get("/api/daily-discover/highlights")
def daily_discover_highlights(
    limit: int = Query(5, ge=1, le=5),
):

    # 設定篩選條件
    condition = ["p.is_active = 1", "v.is_active = 1"]
    where_sql = " AND ".join(condition)

    # 商品資料
    sql = f'''
    SELECT p.id, p.name, p.main_image, MIN(v.price) AS price_cents
    FROM products p JOIN product_variants v ON p.id = v.product_id
    WHERE {where_sql} 
    GROUP BY p.id, p.name, p.main_image 
    ORDER BY p.created_at DESC
    LIMIT %s 
    '''
    # 執行sql
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute(sql, (limit,))
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
    return {"data": data, "count": len(data)}


@app.get("/api/daily-discover")
def daily_discover_highlights(
    pageNumber: int = Query(1, ge=1),
):

    # 設定篩選條件
    condition = ["p.is_active = 1", "v.is_active = 1"]
    where_sql = " AND ".join(condition)

    #算總數 
    total_sql = f'''
    SELECT COUNT(DISTINCT p.id) AS counts
    FROM products p JOIN product_variants v ON p.id = v.product_id
    WHERE {where_sql}
    '''

    # OFFSET
    offset = (pageNumber - 1) * PAGE_SIZE

    # 商品資料
    sql = f'''
    SELECT p.id, p.name, p.main_image, MIN(v.price) AS price_cents
    FROM products p JOIN product_variants v ON p.id = v.product_id
    WHERE {where_sql} 
    GROUP BY p.id, p.name, p.main_image 
    ORDER BY p.created_at DESC
    LIMIT %s OFFSET %s
    '''

    # 執行sql
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute(total_sql)
    total = cur.fetchone()["counts"]
    
    cur.execute(sql, (PAGE_SIZE, offset))
    rows = cur.fetchall()

    has_next = (pageNumber * PAGE_SIZE) < total
    next_pageNumber = pageNumber + 1 if has_next else None


    cur.close()
    conn.close()

    # 建立回傳json
    data = [{
        "id": r["id"],
        "name": r["name"],
        "img": r["main_image"],
        "price": r["price_cents"] // 100 if r["price_cents"] is not None else None}
        for r in rows]
    return {
        "data": data,
        "pageNumber": pageNumber,
        "page_size": PAGE_SIZE,
        "total":total,
        "hasNext": has_next,
        "next_pageNumber": next_pageNumber
        }