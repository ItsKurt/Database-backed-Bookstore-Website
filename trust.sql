CREATE TABLE trust(
	truster VARCHAR(40),
	trustee VARCHAR(40),
	isTrusted BOOL,
	PRIMARY KEY (truster, trustee),
	FOREIGN KEY (truster) REFERENCES users (loginName),
	FOREIGN KEY (trustee) REFERENCES users (loginName));