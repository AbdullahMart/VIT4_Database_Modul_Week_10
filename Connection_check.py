import psycopg2

# Veritabanı bağlantı bilgileri
database_name = "CRM-Project"
user = "postgres"
password = "Kirmizi"
host = "localhost"  # Genellikle localhost veya 127.0.0.1

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

    # İşlemlerinizi gerçekleştirin...

    # Bağlantıyı kapatın
    connection.close()
    print("Bağlantı kapatıldı.")
except Exception as e:
    print("Bağlantı hatası:", e)