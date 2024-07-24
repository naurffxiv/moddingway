package main

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/naurffxiv/moddingway/internal/database"
	"github.com/naurffxiv/moddingway/internal/discord"
	"github.com/naurffxiv/moddingway/internal/util"
)

func main() {
	// env vars
	env := &util.EnvGetter{
		Ok: true,
	}

	dbArgs := database.DbInfo{
		Host: env.GetEnv("POSTGRES_HOST"),
		Port: env.GetEnv("POSTGRES_PORT"),
		User: env.GetEnv("POSTGRES_USER"),
		Password: env.GetEnv("POSTGRES_PASSWORD"),
		DbName: env.GetEnv("POSTGRES_DB"),
	}

	d := &discord.Discord{}

	discordToken := env.GetEnv("DISCORD_TOKEN")

	debug := env.GetEnv("DEBUG")
	debug = strings.ToLower(debug)

	if debug == "true" {
		guildID := env.GetEnv("GUILD_ID")
		modLoggingChannelID := env.GetEnv("MOD_LOGGING_CHANNEL_ID")

		d.Token = discordToken
		d.GuildID = guildID
		d.ModLoggingChannelID = modLoggingChannelID
	} else {
		d.Init(discordToken)
	}

	if !env.Ok { 
		panic(fmt.Errorf("You must supply a %s to start!", env.EnvName))
	}

	d.Conn = database.ConnectToDatabase(dbArgs)
	startDiscord(d)

	// scheduler
	ticker := time.NewTicker(10 * time.Second)
	done := make(chan bool)
	go func() {
		for {
			select {
			case <-done:
				return
			case <-ticker.C:
				scheduledFunctions(d)
			}
		}
	}()
	
	// listen for interrupts and gracefully exit
	fmt.Println("Worker is ready. Press CTRL+C to exit.")
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM, os.Interrupt)
	<-ctx.Done()
	stop()
	done <- true
	d.Session.Close()
	d.Conn.Close()
}

// scheduledFunctions is the collection of functions that are to be run at the specified interval. 
func scheduledFunctions(d *discord.Discord) {
	autoUnexile(d)
}

// startDiscord connects the bot to Discord
// Waits for the functions to be run on ready before returning
func startDiscord(d *discord.Discord) {
	fmt.Printf("Starting Discord...\n")

	err := d.Start()
	if err != nil {
		panic(fmt.Errorf("Could not instantiate Discord: %w", err))
	}

	d.Ready.Add(1)
	d.Session.AddHandler(d.DiscordReady)
	err = d.Session.Open()
	if err != nil {
		panic(fmt.Errorf("Could not open Discord session: %f", err))
	}

	d.Ready.Wait()
}
