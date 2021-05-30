import csv
from connectToDB import Database
import random

input_csv = csv.reader(open("books.csv", encoding='utf-8'))


db = Database.getConnected()


for row in input_csv:
    pub_date = row[10]
    pub_date = pub_date.split('/')
    if not row[0].isdigit():
        continue
    if len(pub_date) == 3:
        title = row[1]
        isbn = row[5]
        language = row[6]
        numPages = row[7]
        publicationDate = pub_date[2]+"-"+pub_date[0]+"-"+pub_date[1]
        publisher = row[11]
        price = round(random.uniform(5.00, 30.00), 2)

        try:
            cur = db.cursor(dictionary=True)
            cur.execute("INSERT INTO books(isbn, price, title, publisher, language, publicationDate, numPages) VALUES(%s, %s, %s, %s, %s, %s, %s)", (isbn, price, title, publisher, language, publicationDate, numPages))
            db.commit()
            cur.close()
        except:
            pass
