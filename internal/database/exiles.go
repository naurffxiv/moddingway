package database

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/naurffxiv/moddingway/internal/enum"
)

type AddExileEntryArgs struct {
	DbUserID    int
	Reason      string
	ExileStatus enum.ExileStatus
	StartTime 	string
	EndTime 	string
}

func AddExileEntryTimed(conn *pgxpool.Pool, p AddExileEntryArgs) (int, error) {
	query := `INSERT INTO exiles (userID, reason, exileStatus, startTimestamp, endTimestamp)
	VALUES ($1, $2, $3, $4, $5)
	RETURNING exileID`
	
	var exileID int
	err := conn.QueryRow(
		context.Background(),
		query,
		p.DbUserID,
		p.Reason,
		p.ExileStatus,
		p.StartTime,
		p.EndTime,
	).Scan(&exileID)
	
	if err != nil {
		return -1, err
	}

	return exileID, nil
}

func AddExileEntryIndefinite(conn *pgxpool.Pool, p AddExileEntryArgs) (int, error) {
	query := `INSERT INTO exiles (userID, reason, exileStatus, startTimestamp)
	VALUES ($1, $2, $3, $4)
	RETURNING exileID`
	
	var exileID int
	err := conn.QueryRow(
		context.Background(),
		query,
		p.DbUserID,
		p.Reason,
		p.ExileStatus,
		p.StartTime,
	).Scan(&exileID)
	
	if err != nil {
		return -1, err
	}

	return exileID, nil
}

// PendingUnexile is the information returned for each exile from GetPendingUnexiles
// this information is used in unexiling a user
type PendingUnexile struct {
	ExileID         int
	DbUserID        string
	ExileStatus     enum.ExileStatus
	DiscordUserID   string
	DiscordGuildID  string
}

// Gets all exiles where the exileStatus is timedExile end timestamp is larger than the current time
// returns it as a slice of PendingExiles.
func GetPendingUnexiles(conn *pgxpool.Pool) ([]PendingUnexile, error) {
	query := `SELECT e.exileID, e.userID, e.exileStatus, u.discordUserID, u.discordGuildID
	FROM exiles e
	JOIN users u ON e.userID = u.userID
	WHERE e.exileStatus = $1 AND e.endTimestamp < $2;`

	rows, err := conn.Query(context.Background(), query, enum.TimedExile, time.Now().UTC().Format(time.RFC3339))
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var pendingUnexiles []PendingUnexile
	for rows.Next() {
		currRow := PendingUnexile{}
		err := rows.Scan(
			&currRow.ExileID,
			&currRow.DbUserID,
			&currRow.ExileStatus,
			&currRow.DiscordUserID,
			&currRow.DiscordGuildID,
		)
		if err != nil {
			return nil, err
		}
		pendingUnexiles = append(pendingUnexiles, currRow)
	}

	return pendingUnexiles, nil
}

func GetUserMostRecentExile(conn *pgxpool.Pool, dbUserID int) (int, error) {
	query := `SELECT exileID FROM exiles
	WHERE userID = $1
	ORDER BY exileID DESC
	LIMIT 1`

	var exileID int
	err := conn.QueryRow(context.Background(), query, dbUserID).Scan(&exileID)
	if err != nil {
		return -1, err
	}
	return exileID, nil
}

func UpdateExileStatus(conn *pgxpool.Pool, exileID int, exileStatus enum.ExileStatus) error {
	query := `UPDATE exiles
	SET exileStatus = $1
	WHERE exileID = $2`

	_, err := conn.Exec(context.Background(), query, exileStatus, exileID)
	return err
}

func RemoveExileEntry(conn *pgxpool.Pool, exileID int) error {
	query := `DELETE FROM exiles
	WHERE exileID = $1`

	_, err := conn.Exec(context.Background(), query, exileID)
	return err
}