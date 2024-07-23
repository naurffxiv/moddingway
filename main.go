package main

import (
	"fmt"
	"os"
	"os/signal"
	"strings"
	"syscall"

	"github.com/naurffxiv/moddingway/internal/discord"
	"github.com/naurffxiv/moddingway/internal/util"
)

func main() {
	env := util.EnvGetter{
		Ok: true,
	}

	d := &discord.Discord{}

	discordToken := env.GetEnv("DISCORD_TOKEN")
	discordToken = strings.TrimSpace(discordToken)

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
	d.Ready.Add(1)
	d.Session.AddHandler(d.DiscordReady)
	err := d.Session.Open()
	if err != nil {
		panic(fmt.Errorf("Could not open Discord session: %f", err))
	}

	d.Ready.Wait()
	d.Session.AddHandler(d.InteractionCreate)
	fmt.Println("Moddingway is ready. Press CTRL+C to exit.")
	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt)
	<-sc

	// Cleanly close down the Discord session.
	d.Session.Close()
}
