import psycopg2
from psycopg2 import sql
import datetime

class Logger:
    # Конструктор по-умолчанию
    def __init__(self, file_name:str):
        self._message:str = ''
        self._file_name:str = file_name + '.log'

    # Запись в лог
    def log(self, message:str):

        # Открываем файл
        with open(self._file_name, 'a', encoding='utf-8') as file:
            
            # Узнаём текущее время
            current_time:str = str(datetime.datetime.now())
            current_time = current_time.split('.')[0]

            # Производим запись сообщения в файл
            file.write(current_time + '\t' + message + '\n')



class DataBase():
    # Конструктор по-умолчанию
    def __init__(self, name:str, user:str, password:str, host:str='localhost', port:str='5432') -> None:
        self._db_name:str = name # Название базы данных
        self._db_user:str = user # Пользователь PostgreSQL
        self._db_password:str = password # Пароль PostgreSQL
        self._db_host:str = host # Адрес базы данных
        self._db_port:str = port # Порт базы данных
        self._logger:Logger = Logger(name) # Логгер
    
    # Создание подключения к БД
    def __connect(self):
        return psycopg2.connect(
                    dbname=self._db_name,
                    user=self._db_user,
                    password=self._db_password,
                    host=self._db_host,
                    port=self._db_port
                )
    
    # Получение списка всех таблиц в БД
    def __get_tables(self) -> list[str]:
        try:
            # Подключаемся к БД 
            with self.__connect() as conn:
                with conn.cursor() as cur:

                    # Выполняем запрос к information_schema
                    cur.execute('''
                        SELECT table_name 
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_type = 'BASE TABLE';
                    ''')
                
                    # Получаем все результаты
                    tables = [row[0] for row in cur.fetchall()]
                    return tables
                
        except (psycopg2.Error, Exception) as e:
            self._logger.log(str(e))
            return []

    # Возвращает список колонок таблицы в порядке их объявления (исключая id)
    def __get_columns(self, table_name: str, id: bool = False) -> list:
        try:
            with self.__connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = %s 
                        ORDER BY ordinal_position
                    """, (table_name,))
                
                    # Исключаем id из списка колонок
                    if id == False:
                        return [row[0] for row in cur.fetchall() if row[0] != 'id']
                    else:
                        return cur.fetchall()
        except (psycopg2.Error, Exception) as e:
            self._logger.log(str(e))
            return []

    # Проверка существования таблицы
    def __checkAvailableTable(self, table_name:str) -> None:
    
        if table_name not in self.__get_tables():
            raise psycopg2.Error(f"Table '{table_name}' does not exist in the database")
        
    def __checkAvailableColums(self, table_name:str, conditions:dict) -> None:

        available_columns = self.__get_columns(table_name, id=True)
        for column in conditions.keys():
            if column not in available_columns:
                raise psycopg2.Error(f"Column '{column}' does not exist")

    # Создание таблицы в БД
    def createTable(self, table_name:str, **columns:str) -> None:
        try:
            # Подключаемся к БД
            with self.__connect() as conn:
                with conn.cursor() as cur:
                    try:
                        # Создание основной таблицы
                        cur.execute(sql.SQL("CREATE TABLE IF NOT EXISTS {} (id SERIAL PRIMARY KEY);").format(sql.Identifier(table_name)))
                
                        # Добавление колонок
                        for col_name, col_type in columns.items():
                            query = sql.SQL("ALTER TABLE {} ADD COLUMN IF NOT EXISTS {} {};").format(
                                sql.Identifier(table_name),
                                sql.Identifier(col_name),
                                sql.SQL(col_type)
                            )
                            cur.execute(query)

                        # Сохраняем изменения
                        conn.commit()
                    except psycopg2.Error as e:
                        self._logger.log(str(e))
                        conn.rollback()

        except (psycopg2.Error, Exception) as e:
            self._logger.log(str(e))


    def insertString(self, table_name: str, **data: str) -> None:
        try:
            # Проверяем существование таблицы
            self.__checkAvailableTable(table_name)
        
            # Получаем список всех существующих колонок
            available_columns = self.__get_columns(table_name)
        
            # Проверяем соответствие колонок
            data_columns = set(data.keys())
            table_columns_set = set(available_columns)
        
            # Проверка существования колонн в таблице
            if not data_columns.issubset(table_columns_set):
                raise psycopg2.Error(f"Some columns are missing from the table")
        
            # Проверка на совпадение кол-ва колонн
            if len(data_columns) != len(available_columns):
                missing_columns = table_columns_set - data_columns
                raise psycopg2.Error("The number of columns transferred does not match the number of columns in the table")
        
            # Подключение к БД
            with self.__connect() as conn:
                with conn.cursor() as cur:

                    # Формируем запрос с правильным порядком колонок
                    values = [data[col] for col in available_columns]
                
                    query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                        sql.Identifier(table_name),
                        sql.SQL(', ').join(map(sql.Identifier, available_columns)),
                        sql.SQL(', ').join([sql.Placeholder()] * len(available_columns))
                    )

                    try:
                        # Выполняем запрос
                        cur.execute(query, values)

                        # Сохраняем изменения
                        conn.commit()
                    except psycopg2.Error as e:
                        self._logger.log(str(e))
                        conn.rollback()
                
        except (psycopg2.Error, Exception) as e:
            self._logger.log(str(e))


    def getString(self, table_name:str, condition:str, params:tuple) -> list[dict]:
        try:
            # Проверяем существование таблицы
            self.__checkAvailableTable(table_name)

            # Подключение к БД
            with self.__connect() as conn:
                with conn.cursor() as cur:

                    # Формируем запрос
                    query = sql.SQL("SELECT * FROM {table} WHERE {conditions}").format(
                        table = sql.Identifier(table_name),
                        conditions = sql.SQL(condition)
                    )

                    # Выполняем запрос
                    cur.execute(query, params)
                    response = cur.fetchall()
                    
                    # Формируем вывод
                    available_columns = self.__get_columns(table_name, id=True)
                    result = []

                    for string in response:
                        data = {}

                        # Формируем словарь для каждой строки ответа
                        for i in range(len(string)):
                            data[available_columns[i][0]] = string[i]

                        # Добавляем словарь в список
                        result.append(data)
                        
                    return result 

        except (psycopg2.Error, Exception) as e:
            self._logger.log(str(e))
            return []
        
    def updateData(self, table_name: str, updates: dict, condition: str, condition_params: tuple) -> None:
        try:
            # Проверяем существование таблицы
            self.__checkAvailableTable(table_name)

            # Проверяем существование колонок
            self.__checkAvailableColums(table_name, updates)

            # Подключение к БД
            with self.__connect() as conn:
                with conn.cursor() as cur:

                    # Безопасное формирование SET части
                    set_parts = []
                    set_values = []
                    for column, value in updates.items():
                        set_parts.append(sql.SQL("{} = %s").format(sql.Identifier(column)))
                        set_values.append(value)
                
                    # Формируем полный запрос
                    query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
                        sql.Identifier(table_name),
                        sql.SQL(', ').join(set_parts),
                        sql.SQL(condition)
                    )
                
                    # Объединяем параметры
                    params = tuple(set_values) + condition_params
                
                    try:
                        # Выполняем запрос
                        cur.execute(query, params)

                        # Сохраняем изменения
                        conn.commit()
                    except psycopg2.Error as e:
                        self._logger.log(str(e))
                        conn.rollback()

        except (psycopg2.Error, Exception) as e:
            self._logger.log(str(e))

    def deleteData(self, table_name: str, conditions: dict) -> None:
        try:
            # Проверяем существование таблицы
            self.__checkAvailableTable(table_name)

            # Проверяем существование колонн
            self.__checkAvailableColums(table_name, conditions)

            # Формируем WHERE часть запроса
            where_parts = []
            where_values = []
            for column, value in conditions.items():
                where_parts.append(sql.SQL("{} = %s").format(sql.Identifier(column)))
                where_values.append(value)

            # Защита от удаления всей таблицы
            if not where_parts:
                raise psycopg2.Error("Delete without conditions is not allowed")

            # Подключаемся к БД
            with self.__connect() as conn:
                with conn.cursor() as cur:
                    
                    # Формируем запрос
                    query = sql.SQL("DELETE FROM {} WHERE {}").format(
                        sql.Identifier(table_name),
                        sql.SQL(' AND ').join(where_parts)
                    )

                    try:
                        # Выполняем запрос
                        cur.execute(query, tuple(where_values))

                        # Сохраняем изменения
                        conn.commit()

                    except psycopg2.Error as e:
                        self._logger.log(str(e))
                        conn.rollback()

        except (psycopg2.Error, Exception) as e:
            self._logger.log(str(e))
