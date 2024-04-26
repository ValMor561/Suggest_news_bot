import psycopg2
from psycopg2.extras import Json
import config
from datetime import datetime

#Класс для подключения к базе данных
class BDRequests():

    #Установка соединения
    def __init__(self):
        self.connection = psycopg2.connect(
            host=config.HOST,
            database=config.DATABASE,
            user=config.USER,
            password=config.PASSWORD,
            client_encoding='utf8'
        )

    def __del__(self):
        self.connection.close()

    def insert_news(self, text, images):
        cursor = self.connection.cursor()
        insert_query = f'INSERT INTO public."ProposedNews" (news_text, images) VALUES (%s, %s) RETURNING id;'
        cursor.execute(insert_query, (text, Json(images)))
        inserted_id = cursor.fetchone()[0]
        self.connection.commit()
        return inserted_id

    def delete_by_id(self, id):
        cursor = self.connection.cursor()
        delete_query = f'DELETE FROM public."ProposedNews" WHERE id = %s;'
        cursor.execute(delete_query, (id, ))
        self.connection.commit()

    def select_all(self):
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM public."ProposedNews";')
        result = cursor.fetchall()
        return result
    
    def select_by_id(self, id):
        cursor = self.connection.cursor()
        select_query = f'SELECT * FROM public."ProposedNews"  WHERE id = %s;'
        cursor.execute(select_query, (id, ))
        result = cursor.fetchone()
        return result
