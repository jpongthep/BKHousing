import sys
import os

import mysql.connector as msql
from mysql.connector import Error

def connect_db():
    try:
        mydb = msql.connect(
            host =os.environ.get("DB_HOST"),
            user = os.environ.get("DB_USER"),
            password = os.environ.get("DB_PASSWORD")
        )
        print("Connect to armis DB")
    except Error as e:
        print("Error while connecting to MySQL", e)

    return mydb

# print(mydb)

if not len(sys.argv) > 1:
    print("no data file !!!")
    print("[help] -> ar_import datafile")
    sys.exit(1)

data_file = sys.argv[1]

armis_db = connect_db()
mycursor = armis_db.cursor()

with open(data_file,"rt", encoding="unicode_escape") as f:
    for line in f:
        data_txt = line.split("$")
        for i, d in enumerate(data_txt):
            if i in [0,1,2,6,8]: 
                if i == 0:
                    year = int(d)-543
                elif i == 1:
                    month = int(d)
                elif i == 2:
                    PersonID = d
                elif i == 6:
                    code = int(d)
                elif i == 8:
                    money = int(d)/100

        try:
            mycursor.execute("""INSERT INTO armis.Payment_financedata (PersonID, date, code, money)
                                VALUES
                                (%s, %s, %s, %s);""", [PersonID, f"{year}-{month}-1", code, money])
            armis_db.commit()
            print(".",end="",flush=True)
        except Error as e:
            print("Error insert into table : ", e)
    print("")
    print("import complete")
    armis_db.close()