begin;

-- clear all data
delete from exiles;
delete from strikes;
delete from users;
delete from notes;
-- seed users
insert into users 
(userid, discordUserID, discordguildid, ismod)
OVERRIDING SYSTEM VALUE
values
(800001, '186259256503173120', '1172230157776466050', false),
(800002, '104917239962046464', '1172230157776466050', false),
(800003, '251577186534817792', '1172230157776466050', false),
(800004, '123124171386388480', '1172230157776466050', false),
(800005, '146406061711032320', '1172230157776466050', false);

-- seed exiles
insert into exiles
(userID, reason, startTimestamp, endTimestamp, exileStatus)
values
(800001, 'short exile, You said a bad word', '2024-11-20 15:15:01.279', '2024-11-20 16:15:01.279', 2),
(800001, 'short exile, More bad words!', '2024-11-20 20:12:55.123', '2024-11-21 02:12:55.123', 2),
(800001, 'Very long active exile', '2024-11-21 12:51:00.123', '2025-11-21 02:12:55.123', 1);

commit;
