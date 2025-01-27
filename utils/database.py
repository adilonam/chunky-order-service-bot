import logging
import os
import psycopg2

def get_item_from_db(item_code):
    try:
        environment = os.getenv('ENVIRONMENT', 'dev')
        print(environment)
        host = 'db' if environment == 'prod' else 'localhost'
        connection = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=host,  # The service name defined in docker-compose.yml
            port='5432'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM products WHERE code = %s", (item_code,))
        item = cursor.fetchone()
        item = {
            'code': item[0],
            'name': item[1],
            'price': float(item[2]),
            'type' : item[3]
        }
        cursor.close()
        connection.close()
        print(item)
        return item
    except Exception as e:
        logging.error(f"Failed to fetch item from database: {e}")
        return None