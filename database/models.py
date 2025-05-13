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

        cursor = connection.cursor()
        create_users_table = '''
            CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            language_code TEXT
            );
            '''
        create_tasks_table = '''
            CREATE TABLE IF NOT EXISTS user_tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id INTEGER,
            task TEXT,
            plan_date DATE,
            done INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
            );
            '''
        create_messages_table = '''
        CREATE TABLE IF NOT EXISTS messages_id(
        id INTEGER PRIMARY KEY NOT NULL,
        user_id INTEGER NOT NULL);
        '''
        cursor.execute(create_users_table)
        cursor.execute(create_tasks_table)
        cursor.execute(create_messages_table)
        connection.commit()
        logging.info("Database created")
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
            records = cursor.fetchall()
            cursor.close()
            return records
        else:
            self._conn.commit()
        cursor.close()
        return True

    async def insert_tasks(
            self, user_id, tasks=None, plan_date=None, done=False
    ):
        """Добавляет задачу в БД."""

        if isinstance(tasks, str):
            tasks = [tasks, ]
        for task in tasks:
            insert_query = '''
            INSERT INTO user_tasks (user_id, task, plan_date, done) 
            VALUES (?, ?, ?, ?);
            '''
            self._execute_query(
                insert_query, user_id, task, plan_date, done
            )
        logging.info(f"Tasks for user {user_id} added")
        return True

    async def select_tasks(
            self, user_id, plan_date=date.today() + timedelta(days=1)
    ):
        """Возвращает список задач пользователя на дату plan_date."""

        select_query = '''
        SELECT id, task FROM user_tasks 
        WHERE user_id = ? 
        AND plan_date = ? 
        AND done = 0
        ORDER BY id;
        '''
        record = self._execute_query(
            select_query, user_id, plan_date, select=True
        )
        if record is not None:
            return record
        return False

    async def update_task(self, user_id, task_id, field, value):
        """Вносит изменения в сведения о задаче."""

        update_query = '''
        UPDATE user_tasks 
        SET ? = ? 
        WHERE id = ? AND user_id = ?;
        '''
        await self._execute_query(
            update_query, field, value, task_id, user_id
        )
        logging.info(f"Task for user {user_id} updated.")

    async def get_task(self, user_id, task_id):
        """Возвращает конкретную задачу."""
        select_query = '''
                SELECT * FROM user_tasks 
                WHERE user_id = ? 
                AND id = ?
                '''
        record = await self._execute_query(
            select_query, user_id, task_id, select=True
        )
        return record

    async def delete_task(self, user_id, task_id):
        """Удаляет задачу из БД."""
        delete_query = '''
        DELETE FROM user_tasks WHERE id = ? AND user_id = ?;
        '''
        self._execute_query(delete_query, task_id, user_id)
        logging.info(f"User's {user_id} task deleted.")
        return True

    async def select_user(self, user_id):
        """Возвращает информацию о пользователе или None."""
        select_query = '''
        SELECT * FROM users 
        WHERE user_id=?
        '''
        record = self._execute_query(
            select_query, user_id, select=True
        )
        if record is not None:
            return record
        return False

    async def insert_user(self, user):
        """Добавляет пользователя в БД."""

        insert_query = '''
        INSERT INTO users (
        user_id, first_name, last_name, username, language_code
        ) 
        VALUES (?, ?, ?, ?, ?);
        '''
        self._execute_query(
            insert_query,
                user.id,
                user.first_name,
                user.last_name,
                user.username,
                user.language_code,
        )
        logging.info(f"User {user.id} added in DB")

    async def insert_message_id(self, user_id, message_id):
        """Добавляет message_id в БД."""
        insert_query = '''
        INSERT INTO messages_id (id, user_id) 
        VALUES (?, ?);
        '''
        self._execute_query(insert_query, message_id, user_id)
        logging.info(f"Message ID for user {user_id} added")
        return True

    async def select_messages_id(self, user_id):
        """Возвращает список message_id добавленных пользователем задач."""
        select_query = '''
        SELECT id FROM messages_id
        WHERE user_id = ?;
        '''
        record = self._execute_query(select_query, user_id, select=True)
        if record is not None:
            return record
        return False

    async def delete_messages_id(self, user_id, messages_id):
        """Удаляет message_id задачи из БД."""
        delete_query = '''
        DELETE FROM messages_id WHERE id = ? AND user_id = ?;
        '''
        for message_id in messages_id:
            self._execute_query(delete_query, *message_id, user_id)
        logging.info(f"User's {user_id} messages deleted.")
        return True


if __name__ == '__main__':
    db = Database('database/db_bot')
    db.create_db()
