import psycopg2
from psycopg2 import sql

def createTable(table_name:str, **columns:str) -> None:
    
    # Подключаемся к бд
    with psycopg2.connect(
            dbname="app_db",
            user="app",
            password="app",
            host="localhost",
            port="5432"
    ) as conn:
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

            

