from connectToDB import Database
import random

subjects = ['Classic', 'Horror', 'Historical Fiction', 'Literature', 'Mystery & Crime', 'Poetry', 'Romance', 'Science Fiction & Fantasy', 'Western', 'Biography', 'History', 'Humor', 'Law']

db = Database.getConnected()
cur = db.cursor()
cur.execute('SELECT isbn FROM books')
books = cur.fetchall()
for book in books:
    subject = random.choice(subjects)
    cur = db.cursor()
    try:
        cur.execute("UPDATE books SET subject = %s WHERE isbn = %s", (random.choice(subjects), book[0]))
        db.commit()
    except:
        pass
    cur.close()