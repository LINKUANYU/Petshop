from typing import List, Optional
from pydantic import BaseModel


class Variant(BaseModel):
    variant_id: int
    sku: str
    label: str
    price: int
    stock: int

class Product_detail(BaseModel):
    product_id: int
    name: str
    description: Optional[str] = None
    brand_id: int
    brand_name: str
    category_id: int
    category_name: str
    category_slug: str
    image: str
    variants: List[Variant]

# 為什麼要用 model（而不是直接 dict）？

# 用 Pydantic model 的好處：

# 結構與型別驗證

# 確保欄位齊全、型別正確（例如 price 一定是 int、stock 一定是 int）。

# DB 回來 None/Decimal/bytes 之類怪型別，會在回應前就被抓到，避免前端收到奇怪 JSON。

# 一致輸出與轉換

# 你可以在 model 或組裝處做統一轉換（例如「分 → 元」的 // 100），保證所有 API 一致。

# 可以用 exclude_none=True、欄位別名（alias）、預設值、Field、validator/serializer（v2）等機制。

# 防資料外洩

# 只會輸出 model 裡定義的欄位，不會把你不小心 SELECT 出來的「內部欄位」一起丟出去。

# 更好的文件與自動化

# response_model＋model 讓 OpenAPI/Swagger 清晰，前端/測試更好對接。

# 可能的代價：

# 會多一點轉型/驗證成本（通常很小），以及寫 model 的工夫。