package database

import (
	"context"
	"fmt"
	"os"

	"github.com/jackc/pgx/v5/pgxpool"
)

// AddOrGetExistingUser returns the userID in the users table of the database.
// If the user does not exist in the table, it will add a new entry and return the userId
// If the user already exists, it will just return the existing userId
func AddOrGetExistingUser(conn *pgxpool.Pool, discordUserID string, discordGuildID string) (int, error) {
	query := `WITH ret AS (
		INSERT INTO users (discordUserId, discordGuildId, ismod)
		VALUES ($1, $2, false)
		ON CONFLICT (discordUserId, discordGuildId) DO NOTHING
		RETURNING userID
	)
	SELECT userID FROM ret
	UNION ALL
	SELECT userID FROM users
	WHERE discordUserId = $1 AND discordGuildId = $2
	LIMIT 1`

	var dbUserID int
	err := conn.QueryRow(context.Background(), query, discordUserID, discordGuildID).Scan(&dbUserID)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Database query failed: %v\n", err)
		return -1, err
	}
	return dbUserID, nil
}