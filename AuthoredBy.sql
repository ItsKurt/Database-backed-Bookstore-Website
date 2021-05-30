CREATE TABLE AuthoredBy(
	author INT NOT NULL,
	book CHAR(13) NOT NULL,
	PRIMARY KEY(author, book),
	FOREIGN KEY(author) REFERENCES authors(authorID),
	FOREIGN KEY(book) REFERENCES books(isbn))