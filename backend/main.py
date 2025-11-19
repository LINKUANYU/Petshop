from pathlib import Path
from fastapi import FastAPI, Query, Request, Depends
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import mysql.connector, os
from typing import List, Optional
from pydantic import BaseModel
from schemas import Product_detail, Variant
from dotenv import load_dotenv
from mysql.connector import Error


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
FRONTEND_DIR = ROOT_DIR / "frontend" 
BACKEND_STATIC = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=TEMPLATES_DIR)



app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name = "frontend")
app.mount("/static", StaticFiles(directory=BACKEND_STATIC), name = "backend-static")


load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# this is a decorator not a real route, it only execute once
@app.on_event("startup")
def test_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT DATABASE(), NOW()")
        row = cur.fetchone()
        print("Current DB is", row[0])
        print("Current time is", row[1])
    # Error provide by mysql connection
    except Error as e:
        print("Connect fail", e)
    finally:
        try:
            if cur:
                cur.close()
            if conn:
                conn.close()
        # if cur/conn have not been define as var will cause NameError, just pass it.
        except NameError:
            pass

#  Use Depends to connect and sending instruction to DB for API
def get_conn():
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def get_cur(conn = Depends(get_conn)):
    cur = conn.cursor(dictionary=True)
    try:
        yield cur
    finally:
        cur.close()

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/daily_discover")
def daily_discover_page(request: Request):
    return templates.TemplateResponse("daily.html", {"request": request})


@app.get("/product/{id}")
def product(
    request: Request,
    id: int
    ):

    
    return templates.TemplateResponse("product.html", {"request": request, "product_id": id})



PAGE_SIZE = 5

@app.get("/api/daily-discover/highlights")
def daily_discover_highlights(
    limit: int = Query(5, ge=1, le=5),
    cur = Depends(get_cur)
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

    cur.execute(sql, (limit,))
    rows = cur.fetchall()


    # 建立回傳json
    data = [{
        "id": r["id"],
        "name": r["name"],
        "img": r["main_image"],
        "price": r["price_cents"] // 100}
        for r in rows]
    return {"data": data, "count": len(data)}


@app.get("/api/daily-discover")
def daily_discover(
    page_number: int = Query(1, ge=1),
    cur = Depends(get_cur)
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
    offset = (page_number - 1) * PAGE_SIZE

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
    cur.execute(total_sql)
    total = cur.fetchone()["counts"]
    
    cur.execute(sql, (PAGE_SIZE, offset))
    rows = cur.fetchall()

    has_next = (page_number * PAGE_SIZE) < total
    next_page_number = page_number + 1 if has_next else None

    # 建立回傳json
    data = [{
        "id": r["id"],
        "name": r["name"],
        "img": r["main_image"],
        "price": r["price_cents"] // 100}
        for r in rows]
    return {
        "data": data,
        "page_number": page_number,
        "page_size": PAGE_SIZE,
        "total":total,
        "has_next": has_next,
        "next_page_number": next_page_number
        }

@app.get("/api/product/{product_id}", response_model=Product_detail)
def get_product_detail(
    product_id: int,
    cur = Depends(get_cur)
    ):
    
    get_product = f'''
        SELECT p.id, p.name, p.description, p.main_image,
            p.brand_id, b.name AS brand_name,
            p.category_id, c.name AS category_name, c.slug AS category_slug
        FROM products p JOIN brands b ON p.brand_id = b.id JOIN categories c ON p.category_id = c.id
        WHERE p.id = %s AND p.is_active = 1 
        '''
    
    cur.execute(get_product, (product_id,))
    data = cur.fetchone()
    if not data:
        raise HTTPException(status_code=404, detail="Product not found")
    if not data["main_image"]:
        data["main_image"] = "assets/Nophoto.png"
    
    
    get_product_variants = f'''
        SELECT id, sku,
            COALESCE(option_text, CONCAT('default-', id)) AS label,
            price, stock_qty AS stock
            FROM product_variants
            WHERE product_id = %s AND is_active = 1
            ORDER BY id
        '''
    
    cur.execute(get_product_variants, (product_id,))
    vrows = cur.fetchall()
    
    variants = [Variant(
        variant_id = v["id"],
        sku = v["sku"],
        label = v["label"],
        price = int(v["price"] // 100),
        stock = int(v["stock"])
        ) for v in vrows]
    
    detail = Product_detail(
        product_id = data["id"],
        name = data["name"],
        description = data.get("description"),
        brand_id = data["brand_id"],
        brand_name = data["brand_name"],
        category_id = data["category_id"],
        category_name = data["category_name"],
        category_slug = data["category_slug"],
        image = data["main_image"],
        variants = variants
    )
    
    return detail
