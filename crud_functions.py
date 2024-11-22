import sqlite3


connection = sqlite3.connect("database2.db")
cursor = connection.cursor()

def initiate_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS  Products(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL, 
    description TEXT,
    price INTEGER NOT NULL
    ); 
    """)
    for i in range(1, 5):
        cursor.execute("INSERT INTO Products(title, description, price) VALUES (?, ?, ?)",
                       (f"Продукт {i}", f"Описание {i}", f"{i * 100}"))
    connection.commit()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS  Users(
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL, 
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        balance INTEGER NOT NULL
        ); 
        """)

def add_user(username, email, age):
    check_user = cursor.execute("SELECT * FROM Users WHERE id = ?", (1,))
    if check_user.fetchone() is None:
        cursor.execute(f"""
        INSERT INTO Users VALUES("{username}", "{email}", "{age}", "{1000}"))
    """)
    cursor.execute("INSERT INTO Users(username, email, age, balance) VALUES (?, ?, ?, ?)",
                   (f"{username}", f"{email}", f"{age}", f"{1000}"))
    connection.commit()

def is_included(username):
    user_in_table = cursor.execute("SELECT username FROM Users").fetchall()
    if username == user_in_table[0]:
        print(user_in_table[0])
        return True
    else:
        return False



def get_all_products():
    initiate_db()
    products = cursor.execute("SELECT * FROM Products").fetchall()

    return products

