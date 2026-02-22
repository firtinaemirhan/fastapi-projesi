from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base # Az önce oluşturduğumuz Base sınıfını çağırıyoruz

class Post(Base):
    __tablename__ = "posts" # Veritabanındaki tablonun adını söylüyoruz

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True) # unique=True: Aynı email ile iki kişi kaydolamaz
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Vote(Base):
    __tablename__ = "votes"
    
    # Composite Primary Key Mantığı:
    # user_id ve post_id kolonlarının ikisi birden 'primary_key=True' olarak ayarlandı.
    # Bu, PostgreSQL'e şu kuralı koyar: "Bir kullanıcı (user_id), aynı post'a (post_id) sadece BİR KEZ kayıt oluşturabilir."
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)