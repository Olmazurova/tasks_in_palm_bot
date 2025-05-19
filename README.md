
# Tasks in palm (bot)
Бот "Задачи на ладони" - бот-планировщик, позволяет запланировать задачи на следующий день.
Каждое день в 9 утра бот присылает список задач на день. 
Через каждые 3 часа спрашивает об их выполнении, задачу можно отметить выполненной или удалить. 
Для любителей отложить дела на завтра тоже есть такая возможность.

### Стек
- aiogram 3
- apscheduler
- fluent
- redis
- sqlite3

## Как развернуть проект локально:
1. Клонировать репозиторий и перейти в него в командной строке:

```git clone https://github.com/Olmazurova/tasks_in_palm_bot.git```

2. Cоздать и активировать виртуальное окружение:

На ОС Linux:
```python3 -m venv .venv```

```source .venv/bin/activate```

```python3 -m pip install --upgrade pip```

На ОС Windows:
```python -m venv .venv```

```source .venv/Scripts/activate```

```python -m pip install --upgrade pip```

3. Установить зависимости из файла requirements.txt:

```pip install -r requirements.txt```

4. Заполнить файл .env необходимыми данными.

5. Запустить проект:

На ОС Linux:
```python3 main.py```

На ОС Windows:
```python main.py```


## TODO

1. Развернуть бот на сервере
2. Добавить возможность настроки бота
3. Добавить возможность планирования задач на любой день (календарь)

---
Автор: Ольга Мазурова
