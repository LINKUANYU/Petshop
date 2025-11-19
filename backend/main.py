from pathlib import Path
from fastapi import FastAPI, Query, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import mysql.connector, os
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

PAGE_SIZE = 5
@app.get("/")
def home(
    request: Request,
    cur = Depends(get_cur)
    ):

    sql = f'''
        SELECT p.id, p.name, p.main_image, MIN(v.price) AS price
        FROM products p JOIN product_variants v ON p.id = v.product_id
        WHERE p.is_active = 1 AND v.is_active = 1
        GROUP BY p.id, p.name, p.main_image
        ORDER BY p.id ASC
        LIMIT %s
        '''
    # 執行sql
    cur.execute(sql, (PAGE_SIZE,))
    data = cur.fetchall()
    
    return templates.TemplateResponse("home.html", {"request": request, "data": data})


@app.get("/daily_discover")
def daily_discover_page(
    request: Request,
    page_number: int = Query(1, ge=1),
    cur = Depends(get_cur)
    ):
    offset = (page_number - 1) * PAGE_SIZE
    
    total_sql = f'''
        SELECT COUNT(*) AS c FROM products WHERE is_active = 1
    '''
    cur.execute(total_sql)
    total = cur.fetchone()

    next_page = total["c"] > page_number * PAGE_SIZE
    previous_page = page_number > 1
    sql = f'''
        SELECT p.id, p.name, p.main_image, MIN(v.price) AS price
        FROM products p JOIN product_variants v ON p.id = v.product_id
        WHERE p.is_active = 1 AND v.is_active = 1
        GROUP BY p.id, p.name, p.main_image
        ORDER BY p.id ASC
        LIMIT %s OFFSET %s
        '''

    cur.execute(sql, (PAGE_SIZE,offset))
    data = cur.fetchall()
    print(data)
    if not data:
        return RedirectResponse(url="/ohoh?msg=page not found", status_code=303)
    
    return templates.TemplateResponse("daily.html", {
        "request": request, 
        "data": data, 
        "page_number": page_number, 
        "next": next_page,
        "previous_page": previous_page
        })


@app.get("/product/{id}")
def product(
    request: Request,
    id: int,
    cur = Depends(get_cur)
    ):
    
    product_sql = f'''
        SELECT 
            p.id AS product_id, p.name AS product_name,
            p.description AS product_description, p.main_image AS image,
            b.id AS brand_id, b.name AS brand_name,
            c.id AS category_id, c.name AS category_name,
            c.slug AS category_slug
        FROM products p JOIN brands b ON p.brand_id = b.id
        JOIN categories c ON p.category_id = c.id
        WHERE p.id = %s AND p.is_active = 1        
    '''
    variant_sql = f'''
        SELECT p.id AS product_id, v.sku, v.option_text, v.price,
            v.stock_qty AS stock
        FROM product_variants v JOIN products p ON v.product_id = p.id
        WHERE p.id = %s AND p.is_active = 1 AND v.is_active = 1
        ORDER BY v.price ASC
    '''

    cur.execute(product_sql, (id,))
    product = cur.fetchone()
    if not product:
        return RedirectResponse(url="/ohoh?msg=product data not found", status_code=303)
    
    cur.execute(variant_sql, (id,))
    variant = cur.fetchall()

    return templates.TemplateResponse("product.html", {
        "request": request, 
        "product_id": id,
        "product": product,
        "variant": variant
        })

@app.get("/ohoh")
def ohoh(request: Request, msg: str):
    return templates.TemplateResponse("ohoh.html", {"request": request, "msg": msg})