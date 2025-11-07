import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "REMOVED_DB_PW",
    "database": "petshop",
}

BRANDS = [
    # name, slug
    ("Royal Canin", "royal-canin"),
    ("Orijen", "orijen"),
    ("Hills Science Diet", "hills-science-diet"),
    ("Wellness", "wellness"),
]

CATEGORIES = [
    # (name, slug, parent_slug)
    ("Dog", "dog", None),
    ("Dog Food", "dog-food", "dog"),
    ("Cat", "cat", None),
    ("Cat Food", "cat-food", "cat"),
]

PRODUCTS = [
    # (name, slug, brand_slug, category_slug, description)
    ("Orijen Original Dog Food", "orijen-original-dog", "orijen", "dog-food",
     "High-protein, grain-free dry dog food."),
    ("Royal Canin Indoor Cat", "royal-canin-indoor-cat", "royal-canin", "cat-food",
     "Dry cat food for adult indoor cats."),
]

VARIANTS = [
    # (product_slug, sku, option_text, price_cents, list_price_cents, weight_g, stock_qty)
    ("orijen-original-dog", "ORJ-ODF-1_5KG", "1.5kg", 1299*100, 1499*100, 1500, 20),
    ("orijen-original-dog", "ORJ-ODF-7KG",   "7kg",   2899*100, 3199*100, 7000, 10),
    ("royal-canin-indoor-cat", "RCN-IC-1_5KG", "1.5kg", 899*100, 1099*100, 1500, 25),
    ("royal-canin-indoor-cat", "RCN-IC-7KG",   "7kg",   2399*100, 2699*100, 7000, 8),
]

def main():
    con = mysql.connector.connect(**DB_CONFIG)
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT DATABASE() AS db")
    row = cur.fetchone()
    print(row)
    if (row or {}).get("db") != "petshop":
        RuntimeError("Database not selected as 'petshop'. Please run schema.sql first")
    
    # brand
    for name, slug in BRANDS:
        cur.execute("""
            INSERT INTO brands (name, slug) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE name = VALUES(name) 
        """, (name, slug)
        )
    print(f"Upsert brands: {cur.rowcount}")

    
    # categoies 
    # parents_id still unknow at first time insertion, "_" no value
    for name, slug, _ in CATEGORIES:
        cur.execute("""
            INSERT INTO categories(name ,slug, parent_id)
            VALUES( %s, %s, NULL)
            ON DUPLICATE KEY UPDATE name = VALUES(name)
        """, (name, slug)
        )
    # check the data just inserted
    cur.execute("SELECT id, slug FROM categories")
    # cur = [{id: 1, slug:dog}, {id: 2, slug: dog-food}]
    
    # build a dict for finding parents_id which is id, slug pairs
    slug_to_id = {} 
    for r in cur.fetchall():
        slug = r["slug"]
        cid = r["id"]
        slug_to_id[slug] = cid
    # slug_to_id = {dog: 1, dog-food: 2}

    # use parents_slug to find parents_id and update table
    for _, slug, parent_slug in CATEGORIES:
        parent_id = slug_to_id.get(parent_slug) if parent_slug else None
        cur.execute("UPDATE categories SET parent_id = %s WHERE slug = %s", (parent_id, slug))
        
    print("Upsert categories & set parent_id")

    # product
    # check brand_slug and categoies_slug for both id
    cur.execute("SELECT id, slug FROM brands")
    brand_map = {r["slug"] : r["id"] for r in cur.fetchall()}
    cur.execute("SELECT id, slug FROM categories")
    categories_map = {r["slug"]: r["id"] for r in cur.fetchall()}

    for name, slug, brand_slug, category_slug, desc in PRODUCTS:
        brand_id = brand_map[brand_slug]
        category_id = categories_map[category_slug]
        cur.execute("""
            INSERT INTO products(name, slug, brand_id, category_id, description, is_active)
            VALUES(%s, %s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
                name        = VALUES(name),
                brand_id    = VALUES(brand_id),
                category_id = VALUES(category_id),
                description = VALUES(description),
                is_active   = 1
        """, (name, slug, brand_id, category_id, desc))
    
    print("Upsert products")

    # product_variants
    cur.execute("SELECT id, slug FROM products")
    product_map = {r["slug"]: r["id"] for r in cur.fetchall()}
    for product_slug, sku, option_text, price_cents, list_price_cents, weight_g, stock_qty in VARIANTS:
        product_id = product_map[product_slug]
        cur.execute("""
                INSERT INTO product_variants(product_id, sku, option_text, price, list_price, weight_g, stock_qty, is_active)
                VALUES(%s, %s, %s, %s, %s, %s, %s, 1)
                ON DUPLICATE KEY UPDATE
                    option_text=VALUES(option_text),
                    price=VALUES(price),
                    list_price=VALUES(list_price),
                    weight_g=VALUES(weight_g),
                    stock_qty=VALUES(stock_qty),
                    is_active=1
            """, (product_id, sku, option_text, price_cents, list_price_cents, weight_g, stock_qty))
    print("Upsert product_variants")

    con.commit()

    # quick check
    cur.execute("SELECT COUNT(*) AS c FROM brands")
    print("brands number: ", cur.fetchone()["c"])
    cur.execute("SELECT COUNT(*) AS c FROM categories")
    print("categories number: ", cur.fetchone()["c"])
    cur.execute("SELECT COUNT(*) AS c FROM products")
    print("product number: ", cur.fetchone()["c"])
    cur.execute("SELECT COUNT(*) AS c FROM product_variants")
    print("product_variants number: ", cur.fetchone()["c"])

    # check data
    cur.execute("""
        SELECT p.name, v.sku, v.option_text, v.price, v.stock_qty
        FROM products p
        JOIN product_variants v
        ON p.id = v.product_id
        ORDER BY p.id, v.id
        LIMIT 5
        """)
    rows = cur.fetchall()
    for row in rows:
        print(f"商品名稱：{row['name']}, 商品編號：{row['sku']}, 內文：{row['option_text']}, ${row['price']/100:,.0f}, (庫存：{row['stock_qty']})")

    cur.close()
    con.close()


if __name__ == "__main__":
    main()