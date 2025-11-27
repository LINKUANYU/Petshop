from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_cur

router = APIRouter(prefix="/api")

PAGE_SIZE = 5
@router.get("/home/product")
def home_product(cur = Depends(get_cur)):

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
    if not data:
        raise HTTPException(status_code=404, detail="查無商品資訊")
    return {"data": data}

