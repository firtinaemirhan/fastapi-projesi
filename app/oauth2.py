from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import schemas, database, models
from .config import settings

# Token'ın nereden geleceğini (login adresi) FastAPI'ye söylüyoruz
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# Sabit metinler yerine ayarlardan çekiyoruz
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    # Orijinal veriyi bozmamak için kopyasını alıyoruz
    to_encode = data.copy()
    
    # Şu anki zamana 30 dakika ekleyip son kullanma tarihi (exp) oluşturuyoruz
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Veriyi, gizli anahtarı ve algoritmayı kullanarak token'ı üretiyoruz
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        # 1. Token'ı çözüyoruz (decode)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. İçindeki user_id'yi alıyoruz
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
            
        # 3. Pydantic şemasından geçiriyoruz
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
        
    return token_data

# Endpoint'lerde kullanacağımız asıl güvenlik kilidi (Dependency)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulanamadı (Token geçersiz veya süresi dolmuş)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Token'ı doğrula
    token_data = verify_access_token(token, credentials_exception)
    
    # Token doğruysa, veritabanından o kullanıcıyı bul ve döndür
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    return user