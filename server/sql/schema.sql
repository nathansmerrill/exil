USE exil;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT AUTO_INCREMENT,
    username VARCHAR(64) NOT NULL,
    password VARCHAR(256) NOT NULL,
    dateJoined DATETIME DEFAULT now(),
    PRIMARY KEY(id)
);
