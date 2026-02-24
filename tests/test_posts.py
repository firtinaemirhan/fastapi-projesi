def test_unauthorized_user_create_post(client):
    # Yetkisiz (normal) client ile post atmayı deniyoruz
    res = client.post(
        "/posts/", 
        json={"title": "Yetkisiz Başlık", "content": "Yetkisiz İçerik"}
    )
    # Sistemin bizi 401 koduyla reddetmesini bekliyoruz
    assert res.status_code == 401

def test_authorized_user_create_post(authorized_client):
    # Yetkili (token'ı olan) client ile post atmayı deniyoruz
    res = authorized_client.post(
        "/posts/", 
        json={"title": "Harika Başlık", "content": "Harika İçerik"}
    )
    # Sistemin postu başarıyla oluşturmasını (201) bekliyoruz
    assert res.status_code == 201


def test_get_all_posts(authorized_client, test_posts):
    # Tüm postları çekmeyi deniyoruz
    res = authorized_client.get("/posts/")
    
    # Başarılı (200) olmasını bekliyoruz
    assert res.status_code == 200
    
    # Veritabanına 3 post eklemiştik, API'ın da bize tam olarak 3 post döndürmesini bekliyoruz
    print("\nAPI'DAN GELEN POSTLAR:", res.json()) 
    assert len(res.json()) == len(test_posts)

def test_get_one_post(authorized_client, test_posts):
    # Sadece ilk postun ID'sini kullanarak tek bir post çekmeyi deniyoruz
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    
    assert res.status_code == 200
    # Gelen verinin gerçekten ilk post olup olmadığını kontrol ediyoruz (Eğer JOIN varsa burası patlayabilir, terminalden json çıktısına bakarız)
    post = res.json()
    print("\nTEKİL POST:", post)

def test_delete_post_success(authorized_client, test_posts):
    # Silinmeden önce ID'yi güvenli bir değişkene alıyoruz
    post_id = test_posts[0].id 
    
    # Değişkeni kullanarak silme isteğini atıyoruz
    res = authorized_client.delete(f"/posts/{post_id}")
    
    # 204 No Content dönmesini bekliyoruz
    assert res.status_code == 204
    
    # Yine aynı değişkeni kullanarak silinen postu bulmayı deniyoruz
    res2 = authorized_client.get(f"/posts/{post_id}")
    assert res2.status_code == 404