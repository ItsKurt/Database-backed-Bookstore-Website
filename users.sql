CREATE TABLE Users(
	loginName VARCHAR(40) NOT NULL,
	firstName VARCHAR(40) NOT NULL,
	lastName VARCHAR(40) NOT NULL,
	password TEXT NOT NULL,
	address TEXT NOT NULL,
	profilePic BLOB,
	phoneNumber VARCHAR(15) NOT NULL,
	isManager BOOL DEFAULT False,
	awarded BOOL DEFAULT False,
	usefulness INT DEFAULT 0,
	numRatings INT DEFAULT 0,
	trustScore INT DEFAULT 0,
	PRIMARY KEY (loginName));