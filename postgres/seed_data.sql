begin;

-- clear all data
delete from notes;
delete from exiles;
delete from strikes;
delete from users;

-- seed users
insert into users 
(userid, discordUserID, discordguildid, ismod,isBanned)
OVERRIDING SYSTEM VALUE
values
(800001, '123456789987654321', '1172230157776466050', false, true),
(800002, '222333444555666777', '1172230157776466050', true, false),
(800003, '888777666555444333', '1172230157776466050', false, false),
(800004, '135792468024681357', '1172230157776466050', false, true),
(800005, '246813579135792468', '1172230157776466050', true, false), 
(800006, '975318642097531864', '1172230157776466050', false, false),
(800007, '111222333444555666', '1172230157776466050', false, true),
(800008, '777888999000111222', '1172230157776466050', true, false), 
(800009, '369258147741852963', '1172230157776466050', false, false),
(800010, '159357486258741963', '1172230157776466050', false, true);


-- seed exiles
insert into exiles
(userID, reason, startTimestamp, endTimestamp, exileStatus)
values
(800001, 'short exile, You said a bad word', '2024-11-20 15:15:01.279', '2024-11-20 16:15:01.279', 2),
(800001, 'short exile, More bad words!', '2024-11-20 20:12:55.123', '2024-11-21 02:12:55.123', 2),
(800001, 'Very long active exile', '2024-11-21 12:51:00.123', '2025-11-21 02:12:55.123', 1);

commit;
