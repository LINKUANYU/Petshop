This project is a petshop website for pratice my software engineer skill.

# PetShop (MVP)
seed.py檔案不完整，後面有補main_image圖檔(暫時需求)，有額外使用SQL syntax 

UPDATE products p JOIN categories c ON p.category_id = c.id SET p.main_image = 'assets/dog.png' WHERE c.slug LIKE 'dog%';

UPDATE products p JOIN categories c ON p.category_id = c.id SET p.main_image = 'assets/cat.png' WHERE c.slug LIKE 'cat%';

# Develop
```bash
cd petshop
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload


