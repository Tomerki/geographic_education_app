import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()


def create_db_pool():
    try:
        conn_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=5,
            user='root',
            password=os.getenv('MYSQL_ROOT_PASSWORD'),
            host='127.0.0.1',
            database='geography',
        )
        return conn_pool
    except mysql.connector.Error as err:
        print(f"Failed to create database connection pool: {err}")
        return None

# Initialize the database pool
db_pool = create_db_pool()