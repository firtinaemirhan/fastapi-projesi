import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app import models  # Bunu dosyanın en üstündeki importların arasına ekle
from app.config import settings # Config dosyanı dahil et

# Sabit metin yerine şifreleri ve bilgileri settings'ten (env) çekiyoruz
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 1. ŞABLON: Sadece veritabanı işlemleri için (Tabloları sil/yarat ve bağlan)
@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. ŞABLON: API'a istek atmak için sahte tarayıcı
@pytest.fixture
def client(session):
    def override_get_db():
        yield session # <-- BURASI DEĞİŞTİ! (try, finally ve close kısımlarını sildik)
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

# 3. ŞABLON: Testlerde kullanmak üzere veritabanına hazır bir kullanıcı ekler
@pytest.fixture
def test_user(client):
    user_data = {"email": "firtina@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    
    assert res.status_code == 201
    new_user = res.json()
    
    # Giriş yaparken kullanabilmek için şifreyi de sözlüğe ekleyip geri döndürüyoruz
    new_user['password'] = user_data['password']
    return new_user
# 4. ŞABLON: Giriş yapmış ve token'ı başlığa (header) eklenmiş yetkili tarayıcı
@pytest.fixture
def authorized_client(client, test_user):
    # Kullanıcı giriş yapar (Eğer API'ın JSON yerine data= bekliyorsa burayı ona göre güncelle)
    res = client.post(
        "/login", 
        json={"email": test_user['email'], "password": test_user['password']} 
    )
    
    # Token'ı al
    token = res.json()["access_token"]
    
    # Client'ın başlıklarına (headers) Authorization'ı ekle
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    
    return client


# 5. ŞABLON: Testler için veritabanına otomatik 3 tane post ekler
@pytest.fixture
def test_posts(test_user, session):
    posts_data = [
        {"title": "1. Harika Post", "content": "Birinci içerik", "owner_id": test_user['id']},
        {"title": "2. Efsane Post", "content": "İkinci içerik", "owner_id": test_user['id']},
        {"title": "3. Mükemmel Post", "content": "Üçüncü içerik", "owner_id": test_user['id']}
    ]
    
    # Verileri SQLAlchemy modeline çevir ve veritabanına topluca ekle
    posts = [models.Post(**post) for post in posts_data]
    session.add_all(posts)
    session.commit()
    
    # Eklenen postları ID'leri atanmış şekilde veritabanından geri çek ve testlere gönder
    posts = session.query(models.Post).all()
    return posts