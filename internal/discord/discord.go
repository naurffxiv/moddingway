package discord

import (
	"fmt"

	"github.com/bwmarrin/discordgo"
)

type Discord struct {
	Token               string
	Session             *discordgo.Session
	ModLoggingChannelID string
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
