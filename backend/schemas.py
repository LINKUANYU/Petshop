from pydantic import BaseModel, EmailStr, Field


# Field
# 用途：對欄位加上限制條件、預設值、描述/範例等中繼資料。
# 你在上面用了 min_length、max_length 來限制字串長度。

class SignupIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=128)

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

class AuthOut(BaseModel):
    ok: bool
    user: UserOut | None = None
    message: str | None = None