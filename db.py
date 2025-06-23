import psycopg2
from psycopg2 import sql

class DataBase():

    # Конструктор по-умолчанию
    def __init__(self, name:str, user:str, password:str, host:str='localhost', port:str='5432') -> None:
        self._db_name:str = name # Название базы данных
        self._db_user:str = user # Пользователь PostgreSQL
        self._db_password:str = password # Парльль PostgreSQL
        self._db_host:str = host # Адрес базы данных
        self._db_port:str = port # Порт базы данных
    
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
                
        except psycopg2.Error as e:
            print(e)
            return []

    # Возвращает список колонок таблицы в порядке их объявления (исключая id)
    def __get_columns(self, table_name: str) -> list:
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
                    return [row[0] for row in cur.fetchall() if row[0] != 'id']
        except psycopg2.Error:
            return []


    # Создание таблицы в БД
    def createTable(self, table_name:str, **columns:str) -> None:
        try:
            # Подключаемся к БД
            with self.__connect() as conn:
                with conn.cursor() as cur:

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
            print(e)


    def insertString(self, table_name: str, **data: str) -> None:
        try:
            # Проверяем существование таблицы
            if table_name not in self.__get_tables():
                raise psycopg2.Error(f"Table '{table_name}' does not exist in the database")
        
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
                
                    cur.execute(query, values)
                    conn.commit()
                
        except psycopg2.Error as e:
            print(f"Database error: {e}")


def main():
    db = DataBase('app_db', 'app', 'app')
    bebra = '1'
    zalupa = '2'