CREATE TABLE BookKeywords(
	book CHAR(13),
	word VARCHAR(20),
	PRIMARY KEY (book, word),
	FOREIGN KEY (book) REFERENCES books(isbn))