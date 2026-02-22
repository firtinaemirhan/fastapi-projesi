from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas, oauth2

router = APIRouter(prefix="/vote", tags=['Vote'])

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    # 1. Aşama: Hedeflenen post veritabanında gerçekten var mı?
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{vote.post_id} numaralı kayıt bulunamadı.")

    # 2. Aşama: Bu kullanıcı daha önce bu post için bir işlem (oy/onay) yapmış mı?
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()

    # 3. Aşama: Kullanıcının talebini işleme alma
    if (vote.dir == 1):
        # Kullanıcı onaylamak istiyor. Zaten onaylamışsa hata döndür.
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Kullanıcı {current_user.id} bu işlemi zaten onayladı.")
        
        # Daha önce onaylamamışsa yeni kayıt oluştur.
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "İşlem başarıyla onaylandı."}
    
    else:
        # Kullanıcı onayını geri çekmek istiyor (dir=0). Eğer ortada bir onay yoksa hata döndür.
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Geri çekilecek bir onay bulunamadı.")
        
        # Onay varsa veritabanından sil.
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Onay başarıyla geri çekildi."}