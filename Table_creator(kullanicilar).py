import psycopg2

# Veritabanı bağlantı bilgileri
database_name = "CRM-Project"
user = "postgres"
password = "Kirmizi"
host = "localhost"

# PostgreSQL veritabanına bağlanma
try:
    connection = psycopg2.connect(
        dbname=database_name,
        user=user,
        password=password,
        host=host
    )
    print("Bağlantı başarılı!")

    # Bağlantı üzerinden bir işlem (cursor) oluşturun
    cursor = connection.cursor()

    # Kullanicilar tablosunu oluşturma sorgusu
    create_table_query = """
        CREATE TABLE IF NOT EXISTS Kullanicilar (
            id SERIAL PRIMARY KEY,
            kullanici VARCHAR(50) NOT NULL UNIQUE,
            parola VARCHAR(50) NOT NULL,
            yetki VARCHAR(20) NOT NULL
        );
    """

    # Tabloyu oluşturma
    cursor.execute(create_table_query)
    connection.commit()
    print("Kullanicilar tablosu başarıyla oluşturuldu.")

    # INSERT sorgusu örneği (Kullanicilar tablosu) - UPSERT işlemi ile
    insert_query = """
        INSERT INTO Kullanicilar (kullanici, parola, yetki)
        VALUES (%s, %s, %s)
        ON CONFLICT (kullanici) DO UPDATE
        SET parola = EXCLUDED.parola,
            yetki = EXCLUDED.yetki;
    """

    # Eklenecek kullanıcıların bilgileri
    kullanici_list = [
        ("ahmet", "werhere", "admin"),
        ("mehmet", "itforever", "user"),
        ("selim", "cyber_warrior", "user"),
        ("a", "b", "admin"),
        ("s", "d", "user")
    ]

    # SQL sorgusunu çalıştırma
    cursor.executemany(insert_query, kullanici_list)

    # Değişiklikleri kaydet
    connection.commit()

    print("Kullanıcı bilgileri başarıyla eklendi!")

    # Bağlantıyı kapatın
    connection.close()
    print("Bağlantı kapatıldı.")
except Exception as e:
    print("Bağlantı hatası:", e)
