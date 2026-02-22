from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint

# Kullanıcı kayıt olurken beklediğimiz yapı
class UserCreate(BaseModel):
    email: EmailStr # Sadece geçerli email formatlarını kabul eder (örn: a@a.com)
    password: str

# Kullanıcıya döneceğimiz güvenli yapı (Şifre YOK!)
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

# 1. Temel Şema: Tüm postlarda ortak olan alanlar
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

# 2. Kullanıcıdan Veri Alırken Kullanılacak Şema (Create/Update)
# PostBase'deki tüm özellikleri miras alır.
class PostCreate(PostBase):
    pass 

# 3. Kullanıcıya Veri Gönderirken Kullanılacak Şema (Response)
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    owner_id: int
    owner: UserOut

    # Pydantic normalde sadece sözlük (dict) anlar. 
    # Bu ayar sayesinde SQLAlchemy'den gelen ORM modellerini de okuyabilir.
    class Config:
        from_attributes = True # Eğer Pydantic V1 kullanıyorsan bu orm_mode = True olmalıdır.

# Kullanıcı giriş yaparken kullanacağımız şema
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Kullanıcıya döneceğimiz Token yapısı
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None # 2. int | None kısmını bu şekilde değiştir


class Vote(BaseModel):
    post_id: int
    # dir (direction): İşlemin yönü. le=1 parametresi ile bu değerin 1 veya daha küçük (0) olmasını zorunlu kılıyoruz.
    # 1: Onayla/Beğen, 0: Onayı/Beğeniyi geri çek.
    dir: conint(le=1) # type: ignore

class PostOut(BaseModel):
    Post: PostResponse
    votes: int

    class Config:
        from_attributes = True
        orm_mode = True