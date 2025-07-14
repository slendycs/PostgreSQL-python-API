[PostgreSQL-python-API](https://github.com/slendycs/PostgreSQL-python-API) - Обёртка для работы с PostgreSQL, позволяющая работать с базой данных избегая написания большинства SQL запросов.

### Начало работы

Для работы библиотеки необходим `psycopg2`:

```
pip install psycopg2-binary
```

### Класс `DataBase`

Работает с PostgreSQL. Автоматически создает логгер с именем БД.

**Параметры конструктора:**  
- `name`: Имя базы данных  
- `user`: Пользователь PostgreSQL  
- `password`: Пароль пользователя  
- `host`: Хост (по умолчанию `localhost`)  
- `port`: Порт (по умолчанию `5432`)  

### Методы  

#### `createTable(table_name: str, **columns: str)`

Создает таблицу или добавляет колонки в существующую.  

**Параметры:**  
   - `table_name`: Имя таблицы  
   - `columns`: Колонки в формате `имя=тип` (например: `name='VARCHAR(255)'`)

**Пример:**
   
   ```python
   db.createTable('users', 
                 name='VARCHAR(50)', 
                 email='VARCHAR(100)')
   ```

#### `insertString(table_name: str, **data: str)`

Вставляет строку в таблицу.  

**Параметры:**  
   - `table_name`: Имя таблицы  
   - `data`: Данные в формате `колонка=значение`  
   *Требует значения для всех колонок (кроме `id`)*

**Пример:**  

   ```python
   db.insertString('users', 
                  name='Alice', 
                  email='alice@example.com')
   ```

#### `getString(table_name: str, condition: str, params: tuple) -> list[dict]`

Выполняет `SELECT` с условием.  

**Параметры:**  
   - `table_name`: Имя таблицы  
   - `condition`: Условие `WHERE` с плейсхолдерами `%s`  
   - `params`: Параметры для условия  
     
**Возвращает:** Список словарей `{колонка: значение}`

**Пример:**

   ```python
   result = db.getString('users', 
                         'name = %s AND age > %s', 
                         ('Alice', 25))
   ```

#### `updateData(table_name: str, updates: dict, condition: str, condition_params: tuple)`

Обновляет данные в таблице.

**Параметры:**  
   - `table_name`: Имя таблицы  
   - `updates`: Словарь `{колонка: новое_значение}`
   - `condition`: Условие `WHERE` с `%s`  
   - `condition_params`: Параметры для условия

**Пример:**

   ```python
   db.updateData('users', 
                {'email': 'new@example.com'}, 
                'id = %s', 
                (1,))
   ```

#### `deleteData(table_name: str, conditions: dict)`

Удаляет строки по условию.  

**Параметры:**  
   - `table_name`: Имя таблицы  
   - `conditions`: Словарь `{колонка: значение}` (условия объединяются через `AND`)  
   *Запрещает удаление без условий*

**Пример:** 
   
   ```python
   db.deleteData('users', {'id': 5})
   ```


### Особенности работы

1. **Автологирование:**  
   Все ошибки автоматически пишутся в файл `{имя_БД}.log`

2. **Безопасность:**  
   - Проверка существования таблиц/колонок
   - Защита от SQL-инъекций через `psycopg2.sql`
   - Блокировка массового удаления (`DELETE` без условий)

3. **Требования к данным:**  
   - `insertString` требует значения для **всех** колонок таблицы (кроме автоинкрементного `id`)
   - Колонки передаются в порядке их объявления в таблице

4. **Обработка ошибок:**  
   - Ошибки не прерывают выполнение программы
   - Все исключения логируются
   - Операции с БД используют транзакции с откатом при ошибках

### Пример использования

```python
from db import DataBase

# Подключение к БД
db = DataBase('my_db', 'admin', 'secure_password')

# Создание таблицы
db.createTable('employees',
               first_name='VARCHAR(50)',
               last_name='VARCHAR(50)',
               salary='INTEGER')

# Вставка данных
db.insertString('employees',
                first_name='John',
                last_name='Doe',
                salary=50000)

# Обновление записи
db.updateData('employees',
              {'salary': 55000},
              'last_name = %s',
              ('Doe',))

# Получение данных
employees = db.getString('employees',
                         'salary > %s',
                         (45000,))
print(employees)  # [{'id':1, 'first_name':'John', ...}]

# Удаление записи
db.deleteData('employees', {'id': 1})
```
