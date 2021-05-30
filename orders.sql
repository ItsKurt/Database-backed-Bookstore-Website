CREATE TABLE orders(
	orderID INT NOT NULL AUTO_INCREMENT,
	customer VARCHAR(40) NOT NULL,
	date_ordered DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (orderID),
	FOREIGN KEY (customer) REFERENCES users(loginName));