from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from passlib.context import CryptContext
from mysql.connector import Error, IntegrityError, errorcode
from ..deps import get_conn, get_cur, get_current_user_id
from ..schemas import SignupIn, SignupOut

# HTTPException
# 用途：當發生業務錯誤或權限不足等情況，需要回 400/401/403/404/409/... 這類錯誤碼時使用。
# 會發生什麼：丟出後，FastAPI 不再執行後續程式碼或路由處理器，直接組出錯誤 JSON。
# 回傳格式（預設）：{"detail": <你給的 detail>}


router = APIRouter(prefix="/api")
pw_context = CryptContext(schemes=["argon2"], deprecated="auto")

# -> str: means this function will return str
def hash_password(plain: str) -> str:
    return pw_context.hash(plain)


@router.post("/signup", response_model = SignupOut)
def signup(payload: SignupIn, conn = Depends(get_conn)):
    cur = conn.cursor(dictionary=True)
    try:
        email = payload.email.strip().lower()
        name = payload.name.strip()
        pw = payload.password
        if len(pw) < 8:
            raise HTTPException(status_code=400, detail="密碼最少為8個字元")

        # 不在後端檢查重複email因為可能同時有兩筆insert進來，直接靠DB去判斷有沒有錯誤

        pw_hash = hash_password(pw)
        cur.execute(
            "INSERT INTO members (name, email, password_hash) VALUES (%s, %s, %s)"
        , (name, email, pw_hash))
        conn.commit()
        # last data's id
        user_id = cur.lastrowid

        return SignupOut(ok = True, message = "註冊成功，請重新登入->")
    
    except IntegrityError as e:                       # 只攔「資料完整性」錯誤（例如 UNIQUE/FK）
        conn.rollback()                               # 這次交易全部撤回，避免半套資料/鎖卡住
        if e.errno == errorcode.ER_DUP_ENTRY:         # 判斷是否為「重複鍵」(MySQL 1062)
            raise HTTPException(status_code=400, detail="已存在email")  # 回給前端 400＋友善訊息

    except Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="資料庫錯誤，請稍後再試")

    finally:
        cur.close()
        