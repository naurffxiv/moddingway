package database

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"
)
type DbInfo struct {
	Host     string
	Port     string
	User     string
	Password string
	DbName   string
}

func ConnectToDatabase(p DbInfo) *pgxpool.Pool {
	dbUrl := fmt.Sprintf("postgres://%s:%s@%s:%s/%s", p.Host, p.Password, p.Host, p.Port, p.DbName)

	fmt.Printf("Connecting to database...\n")
	conn, err := pgxpool.New(context.Background(), dbUrl)
	if err != nil {
		tempstr := fmt.Sprintf("Unable to connect to database: %v\n", err)
		panic(tempstr)
	}
	
	return conn
}
