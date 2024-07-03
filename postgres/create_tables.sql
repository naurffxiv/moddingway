BEGIN;

CREATE TABLE IF NOT EXISTS users (
	userID INT GENERATED ALWAYS AS IDENTITY,
	discordUserID VARCHAR(20) NOT NULL,
	dicordGuildID VARCHAR(20) NOT NULL,
	isMod BOOL NOT NULL,
	PRIMARY KEY(userID)
);

CREATE INDEX IF NOT exists index_discordUserID ON users(discordUserID);


create table if not exists strikes (
	strikeID INT GENERATED ALWAYS AS IDENTITY,
	userID INT NOT null,
	reason text,
	CONSTRAINT fk_user FOREIGN KEY(userID) REFERENCES users(userID)
);


COMMIT;