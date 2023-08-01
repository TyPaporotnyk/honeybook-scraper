from datetime import datetime, timedelta
from typing import Dict

import mysql.connector

from config import DB_DATABASE, DB_HOST, DB_PASSWORD, DB_USER
from prototypes.singleton import Singleton
from utils import create_logger


@Singleton
class DBConnector(object):

    __slots__ = ('conn', 'curr', 'logger')

    def __init__(self):
        self.logger = create_logger("DBConnection")
        self.conn = None
        self.curr = None
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

    def store_db(self, item: Dict):
        self.curr.execute("select * from notifications where source_id = %s", (item['source_id'],))
        result = self.curr.fetchone()

        if not result:
            try:
                self.curr.execute(
                    'INSERT INTO notifications '
                    '(source_id, title, price, location, tags, description, name, type, website, phone, '
                    'email, instagram, facebook, pinterest, snapchat, time_published, created_at) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (*item.values(), datetime.now())
                )

                self.conn.commit()
            except Exception as e:
                self.logger.error(f'Ошибка при загрузке данных в базу данных: {repr(e)}')

    def _get_leads(self, curr_date):
        self.curr.execute("select id, location, title, name from notifications where created_at > %s", (curr_date,))
        result = self.curr.fetchall()
        return result

    def get_new_leeds(self):
        curr_date = datetime.now() - timedelta(hours=0, minutes=30)
        return self._get_leads(curr_date)

    def get_last_30_days_leeds(self):
        curr_date = datetime.now() - timedelta(days=29)
        return self._get_leads(curr_date)
