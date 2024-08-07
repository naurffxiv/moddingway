package database

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"
)

func GetUser(conn *pgxpool.Pool, discordUserID string, discordGuildID string) (int, error) {
	query := `SELECT userID FROM users
	WHERE discordUserId = $1 AND discordGuildID = $2`

	var dbUserID int
	err := conn.QueryRow(context.Background(), query, discordUserID, discordGuildID).Scan(&dbUserID)
	if err != nil {
		return -1, err
	}
	return dbUserID, nil
}

func AddUser(conn *pgxpool.Pool, discordUserID string, discordGuildID string) (int, error) {
	query := `INSERT INTO users (discordUserId, discordGuildId, ismod)
	VALUES ($1, $2, false)
	ON CONFLICT (discordUserId, discordGuildId) DO NOTHING
	RETURNING userID`
	var dbUserID int
	err := conn.QueryRow(context.Background(), query, discordUserID, discordGuildID).Scan(&dbUserID)
	if err != nil {
		return -1, err
	}
	return dbUserID, nil
}