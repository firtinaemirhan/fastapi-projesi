from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10, 
    skip: int = 0, 
    search: Optional[str] = ""
):
    
    # SQLAlchemy Join ve Group By Sorgusu
    # models.Post ve oyların sayısını (func.count) tek bir sorguda çekiyoruz.
    # isouter=True parametresi LEFT OUTER JOIN anlamına gelir (hiç oyu olmayan postlar da gelsin diye).
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    return posts

@router.get("/{id}", response_model=schemas.PostOut) # response_model PostOut olarak güncellendi!
def get_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    # Tek bir post için JOIN ve Group By sorgusu (Bu sefer id'ye göre filtreleniyor)
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} numaralı post bulunamadı")
    
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    # **post.dict() kullanıcının gönderdiği title ve content'i açar.
    # Biz de manuel olarak owner_id'yi current_user.id'den alıp içine ekliyoruz!
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# 1. Giriş yapmayı zorunlu hale getirdik (current_user parametresi eklendi)
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first() # Postu veritabanından çek
    
    # 2. Post var mı kontrolü
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} numaralı post bulunamadı")
    
    # 3. YETKİ KONTROLÜ (En önemli kısım!): Postun sahibi, token'ı gönderen kişi mi?
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu işlemi gerçekleştirmek için yetkiniz yok (Yetkisiz Erişim)!")
    
    # Her şey yolundaysa sil
    post_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostResponse)
# 1. Giriş yapmayı zorunlu hale getirdik
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} numaralı post bulunamadı")
    
    # 2. YETKİ KONTROLÜ: Başkasının postunu güncelleyemez!
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu işlemi gerçekleştirmek için yetkiniz yok (Yetkisiz Erişim)!")
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    
    return post_query.first()