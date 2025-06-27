from db import *

def main():
    db = DataBase('app_db', 'app', 'app')
    db.createTable(
        "Чирикова",
        date="DATE",
        T1_1="TEXT",
        T1_2="REAL",
        T2="REAL",
        T1_T2="TEXT",
        total="REAL",
        warm="REAL",
        hot_water="REAL",
        cold_water="REAL"
    )
    
    # Вставляем данные
    # db.insertString(
    #     "Чирикова",
    #     date="2025-06-22",
    #     T1_1="19-05.44",
    #     T1_2="729.94",
    #     T2="294.17",
    #     T1_T2="22.06.25",
    #     total="1024.12",
    #     warm="0",
    #     hot_water="65.489",
    #     cold_water="37.279"
    # )

    response = db.getString("Чирикова", "date = %s", ("2025-06-22", ))
    # print(response[0])

if __name__ == "__main__":
    main()