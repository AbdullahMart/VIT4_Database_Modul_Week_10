import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Text, BigInteger, Float, Boolean

# Veritabanı bağlantı bilgileri
database_name = "CRM-Project"
user = "postgres"
password = "Kirmizi"
host = "localhost"
table_name = "basvurular"

# CSV dosyasını yükleyin
file_path = '/Users/kudret/Desktop/CRM-Postgresql/csv-file/basvurular.csv'  # Dosyanın tam yolunu belirtin
data = pd.read_csv(file_path, delimiter=';')

# Verilere id sütunu ekle
data.insert(0, 'id', range(1, 1 + len(data)))

# PostgreSQL bağlantı dizesi
connection_string = f"postgresql://{user}:{password}@{host}/{database_name}"

# SQLAlchemy motorunu oluştur
engine = create_engine(connection_string)

# MetaData nesnesini oluştur
metadata = MetaData()

# Pandas veri türlerini SQLAlchemy veri türlerine dönüştüren bir işlev tanımla
def map_dtype(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return Integer
    elif pd.api.types.is_float_dtype(dtype):
        return Float
    elif pd.api.types.is_bool_dtype(dtype):
        return Boolean
    else:
        return Text

# CSV sütunlarını al ve tabloyu tanımla
columns = [Column('id', Integer, primary_key=True)]
for column in data.columns[1:]:
    dtype = map_dtype(data[column].dtype)
    columns.append(Column(column, dtype))

# Tabloyu tanımla
basvurular_table = Table(table_name, metadata, *columns)

# Tabloyu veritabanında oluştur
metadata.create_all(engine)

# Veriyi PostgreSQL tablosuna yaz
data.to_sql(table_name, engine, if_exists='replace', index=False)

print("Veriler başarıyla yüklendi.")
