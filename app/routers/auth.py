from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2 # oauth2 eklendi

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=schemas.Token) # response_model eklendi
def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Geçersiz Kimlik Bilgileri")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Geçersiz Kimlik Bilgileri")

    # --- YENİ EKLENEN KISIM ---
    # Token içine saklamak istediğimiz veri (Payload). Genelde sadece user id yeterlidir.
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    # Bearer, bu token'ın tipini belirtir (sektör standardıdır)
    return {"access_token": access_token, "token_type": "bearer"}