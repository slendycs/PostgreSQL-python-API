from db import *

def main():
    db = DataBase('app_db', 'app', 'app')
    db.createTable(
        "servers",
        server="VARCHAR(100) NOT NULL",
        cost="INTEGER DEFAULT 0",
        rating="REAL"
    )
    
    # Вставляем данные
    db.insertString(
        "servers",
        server="Alpha",
        cost="1500",
        rating="4.7"
    )


if __name__ == "__main__":
    main()