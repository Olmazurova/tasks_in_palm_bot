import sqlite3

# Если в текущей директории нет файла db.sqlite -
# он будет создан; одновременно будет создано и соединение с базой данных.
# Если файл существует, функция connect просто подключится к базе.
con = sqlite3.connect('database/db_bot.sqlite')

cur = con.cursor()

# Готовим SQL-запросы.
# Для читаемости запрос обрамлён в тройные кавычки и разбит построчно.

query_2 = '''
CREATE TABLE IF NOT EXISTS video_products(
    id INTEGER PRIMARY KEY,
    title TEXT,
    product_type TEXT,
    release_year INTEGER
);
'''

# Применяем запросы.

cur.execute(query_2)

# Закрываем соединение с БД.
con.close()

def update_db(user_id, tasks=None, date=None, done=False):
    if isinstance(tasks, str):
        tasks = [tasks,]
    for task in tasks:
        cur.execute(
            'INSERT INTO user_tasks (user_id, task, date, done) VALUES (?, ?, ?, ?)',
            (user_id, task, date, done))
    con.commit()

if __name__ == '__main__':
    con = sqlite3.connect('database/db_bot.sqlite')
    cur = con.cursor()
    create_users_table = '''
    CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY);
    '''
    create_tasks_table = """
    CREATE TABLE IF NOT EXISTS user_tasks(
    id INTEGER AUTOINCREMENT,
    user_id INTEGER,
    task TEXT,
    date INTEGER,
    done INTEGER DEFAULT 0,
    FOREIGN KEY(uset_id) REFERENCES users(user_id)
    );
    """
    cur.executemany(create_users_table, create_tasks_table)
    con.close()