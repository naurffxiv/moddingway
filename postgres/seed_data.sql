BEGIN;

INSERT INTO users (discordUserID, discordGuildID, isMod)
VALUES
('1234567890', '44412345', false),
('9876543210', '44412345', true);

COMMIT;