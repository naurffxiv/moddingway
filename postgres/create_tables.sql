BEGIN;

CREATE TABLE IF NOT EXISTS users (
	userID INT GENERATED ALWAYS AS IDENTITY,
	discordUserID VARCHAR(20) NOT NULL,
	discordGuildID VARCHAR(20) NOT NULL,
	isMod BOOL NOT NULL,
	temporaryPoints INT  not null default 0,
	permanentPoints INT  not null default 0,
	lastInfractionTimestamp TIMESTAMP,
	isBanned BOOL NOT NULL default false,
	PRIMARY KEY(userID),
	UNIQUE(discordUserID, discordGuildID)
);

CREATE INDEX IF NOT EXISTS index_discordUserID ON users(discordUserID);

CREATE TABLE IF NOT EXISTS exiles (
	exileID INT GENERATED ALWAYS AS IDENTITY,
	userID INT NOT null,
	reason TEXT,
	startTimestamp TIMESTAMP,
	endTimestamp TIMESTAMP,
	exileStatus INT NOT NULL,
	PRIMARY KEY(exileID), 
	CONSTRAINT fk_user FOREIGN KEY(userID) REFERENCES users(userID)
);


CREATE TABLE IF NOT EXISTS strikes (
	StrikeID INT GENERATED ALWAYS AS IDENTITY,
	userID INT NOT null,
	severity INT NOT null,
	reason TEXT,
	createdTimestamp TIMESTAMP,
	createdBy VARCHAR(20) NOT NULL,
	lastEditedTimestamp TIMESTAMP,
	lastEditedBy VARCHAR(20) NOT NULL,
	PRIMARY KEY(strikeID),
	CONSTRAINT fk_user FOREIGN KEY(userID) REFERENCES users(userID)
);


CREATE TABLE IF NOT EXISTS notes (
	noteID INT GENERATED ALWAYS AS IDENTITY,
	userID INT NOT null,
	note TEXT,
	CONSTRAINT note_length CHECK (length(note) <= 300),
	createdTimestamp TIMESTAMP,
	createdBy VARCHAR(20) NOT NULL,
	lastEditedTimestamp TIMESTAMP,
	lastEditedBy VARCHAR(20) NOT NULL,
	PRIMARY KEY(noteID),
	CONSTRAINT fk_user FOREIGN KEY(userID) REFERENCES users(userID)
);


CREATE TABLE IF NOT EXISTS roles (
	entryID INT GENERATED ALWAYS AS IDENTITY,
	userID INT NOT null,
	roleID VARCHAR(20) NOT NULL,
	PRIMARY KEY(entryID),
	CONSTRAINT fk_user FOREIGN KEY(userID) REFERENCES users(userID)
);

-- This can be removed after one deploy is run
ALTER TABLE users
 ADD COLUMN IF NOT EXISTS isBanned
 BOOL NOT NULL default false;


COMMIT;