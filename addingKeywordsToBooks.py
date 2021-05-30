from connectToDB import Database
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string


stop_words = set(stopwords.words('english'))

db = Database.getConnected()
cur = db.cursor(dictionary=True)
cur.execute('SELECT isbn, title FROM books')
books = cur.fetchall()
cur.close()
for book in books:
    tokens = word_tokenize(book['title'])
    keywords = [word.lower() for word in tokens if word not in stop_words and word not in string.punctuation]
    cur = db.cursor(dictionary=True)
    for keyword in set(keywords):
        try:
            cur.execute("INSERT INTO bookkeywords (word, book) VALUES (%s, %s)", (keyword, book['isbn']))
            db.commit()
        except:
            pass
    cur.close()