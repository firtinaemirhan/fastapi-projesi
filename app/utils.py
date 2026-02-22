import bcrypt

def hash(password: str):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')

# utils.py dosyasının mevcut hali (hash fonksiyonu) duracak, altına bunu ekle:

def verify(plain_password, hashed_password):
    # Kullanıcının girdiği şifreyi ve veritabanındaki şifreyi byte'a çevirip karşılaştırıyoruz
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))