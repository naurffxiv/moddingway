BEGIN;

CREATE TABLE IF NOT EXISTS users (
	userID INT GENERATED ALWAYS AS IDENTITY,
	discordUserID VARCHAR(20) NOT NULL,
	discordGuildID VARCHAR(20) NOT NULL,
	userRole SMALLINT NOT NULL default 1,
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

CREATE TABLE IF NOT EXISTS forms (
	formID INT GENERATED ALWAYS AS IDENTITY,
	userID INT NOT null,
	reason TEXT,
	approval BOOL,
	approvedByUserID INT,
	createdTimestamp TIMESTAMP,
	PRIMARY KEY(formID),
	CONSTRAINT fk_user FOREIGN KEY(userID) REFERENCES users(userID)
);

-- This can be removed after one deploy is run

-- Messy setup that allows us to do conditional logic in this postgres call
DO
$do$
BEGIN
   IF exists (SELECT 1 	FROM information_schema.columns WHERE table_name='users' AND column_name='ismod') THEN
		-- add role column
   		alter table users add userRole SMALLINT NOT NULL default 1;

		-- set current mods to mod role
		update users set
			userRole = 2
			where ismod;
	
		-- remove old column
		alter table users drop column ismod;
   END IF;
END;
$do$;

COMMIT;