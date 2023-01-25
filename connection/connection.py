from config import DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE
from prototypes.singleton import Singleton
from datetime import datetime, timedelta
import mysql.connector

from utils import create_logger

@Singleton
class DBConnector(object):
    def __init__(self):
        self.logger = create_logger("DBConnection")
        self.create_connection()

    def __str__(self):
        return 'Database connection object'

    def create_connection(self):
        self.conn = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_DATABASE
        )

        self.curr = self.conn.cursor()
        self.logger.info('Соединение было установлено')


    def store_db(self, item):
        self.curr.execute("select * from notifications where source_id = %s", (item['source_id'],))
        result = self.curr.fetchone()

        if not result:
            try:
                self.curr.execute('INSERT INTO notifications '\
                                ' (source_id, title, price, location, tags, description, name, type, website, phone, email, instagram, facebook, pinterest, snapchat, time_published, created_at)'\
                                ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',(
                                    item['source_id'],
                                    item['title'],
                                    item['price'],
                                    item['location'],
                                    item['tags'],
                                    item['description'],
                                    item['name'],
                                    item['type'],
                                    item['website'],
                                    item['phone'],
                                    item['email'],
                                    item['instagram'],
                                    item['facebook'],
                                    item['pinterest'],
                                    item['snapchat'],
                                    item['time_published'],
                                    datetime.now()))

                self.conn.commit()
            except Exception as e:
                self.logger.error('Ошибка при загрузке данных в базу данных')

    def get_new_leeds(self):
        curr_date = datetime.now() - timedelta(hours=0, minutes=30)
        # curr_date = datetime.now() - timedelta(days=29)
        self.curr.execute("select id, location, title, name from notifications where created_at > %s", (curr_date,))

        result = self.curr.fetchall()

        return result