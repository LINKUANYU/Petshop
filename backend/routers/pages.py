from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi import APIRouter, Depends, Request, Query
from ..deps import get_conn, get_cur, get_current_user_id
from ..path import TEMPLATES_DIR

templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter()

PAGE_SIZE = 5
@router.get("/")
def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/ohoh")
def ohoh_page(request: Request, msg: str):
    return templates.TemplateResponse("ohoh.html", {"request": request, "msg": msg})

@router.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/daily_discover")
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
    if not data:
        return RedirectResponse(url="/ohoh?msg=page not found", status_code=303)
    
    return templates.TemplateResponse("daily.html", {
        "request": request, 
        "data": data, 
        "page_number": page_number, 
        "next": next_page,
        "previous_page": previous_page
        })


@router.get("/product/{id}")
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

