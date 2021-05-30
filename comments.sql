CREATE TABLE Comments(
	c_text TEXT,
	c_date DATETIME DEFAULT CURRENT_TIMESTAMP,
	bookRating INT(2) NOT NULL,
	CHECK (bookRating > -1 AND bookRating < 11),
	creator VARCHAR(40) NOT NULL,
	book CHAR(13) NOT NULL,
	commentID INT NOT NULL AUTO_INCREMENT,
	useless INT DEFAULT 0,
	usefull INT DEFAULT 0,
	v_usefull INT DEFAULT 0,
	PRIMARY KEY (commentID),
	FOREIGN KEY (creator) REFERENCES users(loginName),
	FOREIGN KEY (book) REFERENCES books(isbn))