import mysql.connector.pooling
from google.cloud.sql.connector import Connector

# Set the connection parameters
user = 'luckypig2023'
password = 'LuckypigProject#1'
database = 'Luckypig database'
instance_connection_name = "luckypig-consulting:us-central1:luckypig2023"

# Create a connection pool
config = {
    'user': user,
    'password': password,
    'database': database,
    'pool_name': 'mypool',
    'pool_size': 5,
    'host': '34.30.103.41',
}
pool = mysql.connector.pooling.MySQLConnectionPool(**config)

connector = Connector()
# Define a function to create connections using the Cloud SQL connector
conn = connector.connect(instance_connection_string=f"mysql+pymysql://{user}:{password}@/{database}?unix_socket=/cloudsql/{instance_connection_name}", driver='pymysql')

# Create a SQLAlchemy engine that uses the connection pool
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://', creator=conn)

# Use the engine to execute queries
with engine.connect() as conn:
    result = conn.execute('SELECT * FROM user')
    for row in result:
        print(row)
