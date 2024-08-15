package database

import (
	"context"
	"fmt"
	"os"

	"github.com/jackc/pgx/v5/pgxpool"
)

type DbInfo struct {
	Host     string
	Port     string
	User     string
	Password string
	DbName   string
}


const (
	// assumes root of the project folder is the working directory when run
	dbPopulatePath = "./postgres/create_tables.sql"
)

func ConnectToDatabase(p DbInfo) *pgxpool.Pool {
	dbUrl := fmt.Sprintf("postgres://%s:%s@%s:%s/%s", p.User, p.Password, p.Host, p.Port, p.DbName)

	fmt.Printf("Connecting to database...\n")
	conn, err := pgxpool.New(context.Background(), dbUrl)
	if err != nil {
		tempstr := fmt.Sprintf("Unable to connect to database: %v\n", err)
		panic(tempstr)
	}

	return conn
}

func PopulateDatabase(conn *pgxpool.Pool) {
	init_sql, err := os.ReadFile(dbPopulatePath)
	if err != nil {
		tempstr := fmt.Sprintf("Unable to read DB init file: %v\n", err)
		panic(tempstr)
	}

	_, err = conn.Exec(context.Background(), string(init_sql))
	if err != nil {
		tempstr := fmt.Sprintf("Unable to populate DB with initial tables: %v\n", err)
		panic(tempstr)
	}
}