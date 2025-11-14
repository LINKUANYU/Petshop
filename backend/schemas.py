from typing import List, Optional
from pydantic import BaseModel
# 型別設定


 # 以下待確認
class Variant(BaseModel):
    id: int
    sku: str
    label: str
    # 建議：全專案決定是「元」還是「分」
    price: Optional[int] = None   # 例如回整數「元」，如果沒有就 None
    stock: int

class Product_detail(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    brand_id: int
    brand_name: str
    category_id: int
    category_name: str
    category_slug: str
    photo: str
    variants: List[Variant]