def test_root(client):
    res = client.get("/")
    assert res.status_code == 200

def test_create_user(client):
    res = client.post(
        "/users/", 
        json={"email": "test1234@gmail.com", "password": "password123"}
    )
    assert res.status_code == 201


from jose import jwt
from app.config import settings

def test_login_user(client, test_user):
    # FastAPI'nin OAuth2PasswordRequestForm yapısı JSON değil, 'data' (Form-Data) bekler
    res = client.post(
        "/login", 
        data={"username": test_user['email'], "password": test_user['password']}
    )
    
    login_res = res.json()
    
    assert res.status_code == 200
    assert "access_token" in login_res
    assert login_res["token_type"] == "bearer"

def test_login_user(client, test_user):
    res = client.post(
        "/login", 
        json={"email": test_user['email'], "password": test_user['password']} # <-- BURASI DEĞİŞTİ
    )
    
    print("\nAPI YANITI:", res.json()) # Eğer patlarsa gerçek hatayı ekranda görelim
    
    login_res = res.json()
    assert res.status_code == 200
    assert "access_token" in login_res
    assert login_res["token_type"] == "bearer"

def test_login_user_incorrect_password(client, test_user):
    res = client.post(
        "/login", 
        json={"email": test_user['email'], "password": "yanlis_sifre_123"} # <-- BURASI DEĞİŞTİ
    )
    
    print("\nYANLIŞ ŞİFRE YANITI:", res.json())
    assert res.status_code == 403