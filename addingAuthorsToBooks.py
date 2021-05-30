import csv
from connectToDB import Database


input_csv = csv.reader(open("books.csv", encoding='utf-8'))

db = Database.getConnected()
cur = db.cursor()
for row in input_csv:
    pub_date = row[10]
    pub_date = pub_date.split('/')
    if not row[0].isdigit():
        continue
    if len(pub_date) == 3:
        authors = row[2]
        authors = authors.split('/')
        for author in authors:
            try:
                cur = db.cursor()
                cur.execute("INSERT INTO authors (name, book) VALUES (%s, %s)", (author, row[5]))
                db.commit()
            except:
                pass
        cur.close()