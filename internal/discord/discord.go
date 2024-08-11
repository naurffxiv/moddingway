package discord

import (
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Discord struct {
	Token               string
	Session             *discordgo.Session
	Ready               sync.WaitGroup
	GuildID             string
	ModLoggingChannelID string
	Conn                *pgxpool.Pool

	// The structure of the following map is Roles[guild_id][role_name]
	Roles map[string]map[string]*discordgo.Role
}

func (d *Discord) Init(token string) {
	d.Token = token
	d.GuildID = DefaultGuildID
	d.ModLoggingChannelID = DefaultModLoggingChannel
}

// Start sets up the token and intents of the bot before it logs in
// Intents are what events the bot is subscribed to, so it will
// be notified of any events within the selected categories
// IntentGuilds - events related to the configuration of roles, channels, threads
// IntentGuildMembers - events related to new members/members leaving
// IntentGuildModeration - events related to audit log entries and bans
// IntentGuildMessageReactions - events related to reactions (needed for role reactions)
// Some of these might not be needed given that most logging will be done with YAGPDB
func (d *Discord) Start() error {
	s, err := discordgo.New("Bot " + d.Token)
	if err != nil {
		return fmt.Errorf("Could not start Discord: %f", err)
	}

	s.Identify.Intents = discordgo.IntentGuilds | discordgo.IntentGuildMembers | discordgo.IntentGuildModeration | discordgo.IntentGuildMessageReactions

	d.Session = s
	return nil
}

// DiscordReady initializes the bot and blocks the bot from proceeding until
// initialization finishes
func (d *Discord) DiscordReady(s *discordgo.Session, event *discordgo.Ready) {
	defer d.Ready.Done()
	d.AddCommands(s, event)
	d.MapExistingRoles(s, event)
}

// MapExistingRoles takes the existing roles from all guilds the bot is in
// and populates the Roles map
func (d *Discord) MapExistingRoles(s *discordgo.Session, event *discordgo.Ready) {
	log.Printf("Mapping existing roles...\n")

	d.Roles = make(map[string]map[string]*discordgo.Role)

	log.Printf("Found the following roles:\n")
	for _, discordGuild := range event.Guilds {
		guildID := discordGuild.ID
		existingRoles := discordGuild.Roles
		d.Roles[guildID] = make(map[string]*discordgo.Role)
		log.Printf("Guild %v:\n", guildID)
		for _, role := range existingRoles {
			d.Roles[guildID][role.Name] = role
			log.Printf("%v, ", role.Name)
		}
		log.Printf("\n")
	}
}

// StartInteraction is a helper function that responds to the user who invoked
// the slash command ephemerally with the string message
func StartInteraction(s *discordgo.Session, i *discordgo.Interaction, message string) error {
	err := s.InteractionRespond(i, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: message,
			Flags:   discordgo.MessageFlagsEphemeral,
		},
	})
	return err
}

// ContinueInteraction provides an additional ephemeral response to an interaction
func ContinueInteraction(s *discordgo.Session, i *discordgo.Interaction, message string) error {
	_, err := s.FollowupMessageCreate(i, true, &discordgo.WebhookParams{
		Content: message,
		Flags:   discordgo.MessageFlagsEphemeral,
	})
	return err
}

// RespondToInteraction is a helper function that decides whether StartInteraction
// or ContinueInteraction should be used
func RespondToInteraction(s *discordgo.Session, i *discordgo.Interaction, message string, isFirstInteraction *bool) error {
	interactionTimestamp, err := discordgo.SnowflakeTimestamp(i.ID)
	if err != nil {
		return err
	}
	if *isFirstInteraction {
		if (3 * time.Second) <= time.Since(interactionTimestamp) {
			return fmt.Errorf("initial interaction timeout")
		}
		err := StartInteraction(s, i, message)
		if err == nil {
			*isFirstInteraction = false
		}
		return err
	} else {
		if (15 * time.Minute) <= time.Since(interactionTimestamp) {
			return fmt.Errorf("followup interaction timeout")
		}
		return ContinueInteraction(s, i, message)
	}
}
