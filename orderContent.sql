CREATE TABLE orderContent(
	orderID INT NOT NULL,
	book CHAR(13),
	copies INT NOT NULL,
	customer VARCHAR(40) NOT NULL,
	PRIMARY KEY (orderID, book),
	FOREIGN KEY (book) REFERENCES books(isbn),
	FOREIGN KEY (orderID) REFERENCES orders(orderID));