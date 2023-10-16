import sqlite3
connect = sqlite3.connect('bd.db')
cursor = connect.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS "users" ("id" Integer not null, "tg_id" Integer not null, primary key("id" AUTOINCREMENT));''')
connect.commit()
cursor.execute('''CREATE TABLE IF NOT EXISTS "categories" ("id" Integer not null, "name" Text not null, primary key("id" AUTOINCREMENT));''')
connect.commit()

arr = ["business", "entertainment", "general", "health" , "science", "sports", "technology"]
i=0
res = cursor.execute(''' SELECT * FROM "categories"''').fetchall()

if(res == 0):
    while i < len(arr):

        cursor.execute(''' INSERT INTO "categories"(name) VALUES(?)''',[arr[i]])
        connect.commit()
        i = i+1

cursor.execute('''CREATE TABLE IF NOT EXISTS "subscribes" ("user_id" Integer not null, "category_id" Integer not null);''')
connect.commit()
