from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import mysql.connector, os
from mysql.connector import Error
from starlette.middleware.sessions import SessionMiddleware
from .deps import DB_CONFIG
from .routers import member, pages, product
from .path import FRONTEND_DIR, BACKEND_STATIC

app = FastAPI()

app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name = "frontend")
app.mount("/static", StaticFiles(directory=BACKEND_STATIC), name = "backend-static")

app.include_router(member.router)
app.include_router(pages.router)
app.include_router(product.router)

SECRET_KEY = os.getenv("SECRET_KEY")
app.add_middleware(
    SessionMiddleware,
    secret_key = SECRET_KEY,
    same_site="lax",
    https_only=False
)

# this is a decorator not a real route, it only execute once
@app.on_event("startup")
def test_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT DATABASE()")
        row = cur.fetchone()
        print("Current DB is", row[0])
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

