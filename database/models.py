import sqlite3
import logging
import os
from datetime import date, timedelta

class Database:
    """ Класс работы с базой данных """
    def __init__(self, name):
        self.name = name
        self._conn = self.connection()
        logging.info("Database connection established")

    def create_db(self):
        """Создание базы данных и таблиц в ней."""
        connection = sqlite3.connect(f"{self.name}.sqlite")
        logging.info("Database created")
        cursor = connection.cursor()
        create_users_table = '''
            CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            name TEXT
            );
            '''
        create_tasks_table = '''
            CREATE TABLE IF NOT EXISTS user_tasks(
            id INTEGER AUTOINCREMENT,
            user_id INTEGER,
            task TEXT,
            plan_date INTEGER,
            done INTEGER DEFAULT 0,
            FOREIGN KEY(uset_id) REFERENCES users(user_id)
            );
            '''
        cursor.executemany(create_users_table, create_tasks_table)
        connection.commit()
        cursor.close()

    def connection(self):
        """Проверяет создана ли база данных и подключается к ней."""

        db_path = os.path.join(os.getcwd(), f"{self.name}.sqlite")
        if not os.path.exists(db_path):
            self.create_db()
        return sqlite3.connect(f"{self.name}.sqlite")

    def _execute_query(self, query, *args, select=False):
        """Обрабатывает запросы к БД."""

        cursor = self._conn.cursor()
        cursor.execute(query, args)
        if select:
            records = cursor.fetchone()
            cursor.close()
            return records
        else:
            self._conn.commit()
        cursor.close()

    async def insert_tasks(
            self, user_id, tasks=None, planning_date=None, done=False
    ):
        """Добавляет задачу в БД."""

        if isinstance(tasks, str):
            tasks = [tasks, ]
        for task in tasks:
            insert_query = '''
            INSERT INTO user_tasks (user_id, task, plan_date, done) 
            VALUES (?, ?, ?, ?);'''
            await self._execute_query(
                insert_query, (user_id, task, planning_date, done)
            )
        logging.info(f"Tasks for user {user_id} added")

    async def select_tasks(
            self, user_id, plan_date=date.today() + timedelta(days=1)
    ):
        """Возвращает список задач пользователя на дату plan_date."""

        select_query = '''
        SELECT task FROM user_tasks 
        WHERE user_id = ? 
        AND plan_date = ? 
        AND done = 0
        ORDER BY task;
        '''
        record = await self._execute_query(
            select_query, (user_id, plan_date), select=True
        )
        return record

    async def update_tasks(self, user_id, task_id, field, value):
        """Вносит изменения в сведения о задаче."""

        update_query = '''
        UPDATE user_tasks 
        SET ? = ? 
        WHERE id = ? AND user_id = ?;
        '''
        await self._execute_query(
            update_query, (field, value, task_id, user_id)
        )
        logging.info(f"Task for user {user_id} updated.")

    async def delete_task(self, user_id, task_id):
        """Удаляет задачу из БД."""

        delete_query = '''
        DELETE FROM user_tasks WHERE id = ? AND user_id = ?;
        '''
        self._execute_query(delete_query, (task_id, user_id))
        logging.info(f"User's {user_id} task deleted.")
