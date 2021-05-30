CREATE TABLE cart(
	cart_owner VARCHAR(40) NOT NULL,
	book CHAR(13),
	copies INT DEFAULT 1,
	PRIMARY KEY (cart_owner, book),
	FOREIGN KEY (book) REFERENCES books(isbn),
	FOREIGN KEY (cart_owner) REFERENCES users(loginName));