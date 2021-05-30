SELECT DISTINCT * FROM books, authors, (SELECT DISTINCT a2.NAME FROM authors a1, authors a2 WHERE a1.name = 'Stephen King' AND a1.name != a2.name AND a1.book = a2.book)d1 WHERE authors.name = d1.name AND authors.book = isbn