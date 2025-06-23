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

    # Возвращает список колонок таблицы
    def __get_columns(self, table_name: str, schema: str = 'public') -> list:
        try:
            with self.__connect() as conn:
                with conn.cursor() as cur:

                    # Параметризованный запрос
                    cur.execute('''
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_schema = %s 
                        AND table_name = %s 
                        ORDER BY ordinal_position;
                    ''', (schema, table_name))
                
                    # Возвращаем список колонок (имя_колонки)
                    return cur.fetchall()
                
        except psycopg2.Error as e:
            print(e)
            return []


    # Создание таблицы в бд
    def createTable(self, table_name:str, **columns:str) -> None:
        try:
            # Подключаемся к бд
            with self.__connect() as conn:
                with conn.cursor() as ptr:

                    # Создание основной таблицы
                    ptr.execute(sql.SQL("CREATE TABLE IF NOT EXISTS {} (id SERIAL PRIMARY KEY);").format(sql.Identifier(table_name)))
                
                    # Добавление колонок
                    for col_name, col_type in columns.items():
                        query = sql.SQL("ALTER TABLE {} ADD COLUMN IF NOT EXISTS {} {};").format(
                            sql.Identifier(table_name),
                            sql.Identifier(col_name),
                            sql.SQL(col_type)
                        )
                        ptr.execute(query)

                    # Сохраняем изменения
                    conn.commit()

        except psycopg2.Error as e:
            print(e)


    # def insertItem(self, table_name:str) -> None:
    #     try:
    #         # Проверяем существование таблицы в бд
    #         if table_name in self.__get_tables():

    #             # Подключаемся к бд
    #             with self.__connect() as conn:
    #                 with conn.cursor() as ptr:

    #                     query = sql.SQL("INSERT INTO {} ()").format(
    #                         sql.Identifier(table_name),

    #                     )

    #     except psycopg2.Error as e:
    #         print(e)



def main():
    db = DataBase('app_db', 'app', 'app')