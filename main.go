package main

import (
	"fmt"
	"os"
	"os/signal"
	"strings"
	"syscall"

	"github.com/naurffxiv/moddingway/internal/discord"
)

func main() {
	discordToken, ok := os.LookupEnv("DISCORD_TOKEN")
	if !ok {
		panic("You must supply a DISCORD_TOKEN to start!")
	}
	discordToken = strings.TrimSpace(discordToken)

	d := &discord.Discord{
		Token:        discordToken,
		LogChannelID: "",
	}

	fmt.Printf("Starting Discord...\n")
	err := d.Start()
	if err != nil {
		panic(fmt.Errorf("Could not instantiate Discord: %w", err))
	}
	defer d.Session.Close()
	start(d)
}

// start adds all the commands and connects the bot to Discord.
// Listens for CTRL+C then terminates the connection.
func start(d *discord.Discord) {
	d.Session.AddHandler(d.AddCommands)
	err := d.Session.Open()
	if err != nil {
		panic(fmt.Errorf("Could not open Discord session: %f", err))
	}

	d.Session.AddHandler(d.InteractionCreate)

	fmt.Println("Moddingway is ready. Press CTRL+C to exit.")
	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt)
	<-sc

	// Cleanly close down the Discord session.
	d.Session.Close()
}
