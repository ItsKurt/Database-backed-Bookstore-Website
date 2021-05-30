import mysql.connector


class Database:
    def getConnected():
        db = mysql.connector.connect(
            host='localhost',
            user='431user',
            passwd='bookstore',
            database='Bookstore'
        )
        return db
