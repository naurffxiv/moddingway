package discord

import (
	"fmt"
	"regexp"
	"strconv"
	"time"

	"github.com/bwmarrin/discordgo"
)

// mapOptions is a helper function that creates a map out of the arguments used in the slash command
func mapOptions(i *discordgo.InteractionCreate) map[string]*discordgo.ApplicationCommandInteractionDataOption {
	options := i.ApplicationCommandData().Options
	optionMap := make(map[string]*discordgo.ApplicationCommandInteractionDataOption, len(options))
	for _, opt := range options {
		optionMap[opt.Name] = opt
	}
	return optionMap
}

// parseDuration parses the string provided and returns the time.Duration equivalent
// does not support negative durations
func parseDuration(userInput string) (time.Duration, error) {
	const maxDuration time.Duration = 1<<63 - 1
	// matches any string that is a string of numbers followed by a single letter
	r, _ := regexp.Compile(`^([\d]+)([a-zA-Z]{1})$`)

	// groups[0] is the entire match, following elements are capture groups
	groups := r.FindStringSubmatch(userInput)
	if len(groups) < 2 {
		err := fmt.Errorf("invalid format")
		return 0, err
	}
	num, err := strconv.ParseInt(groups[1], 10, 64)
	if err != nil {
		return 0, err
	}

	// get duration based on unit
	var factor time.Duration
	switch groups[2] {
	case "s":
		factor = time.Second
	case "m":
		factor = time.Minute
	case "h":
		factor = time.Hour
	case "d":
		factor = time.Hour * 24
	case "w":
		factor = time.Hour * 24 * 7
	// month overlaps with minutes, favoring using something like "30d" to specify a month
	case "y":
		factor = time.Hour * 24 * 365
	default:
		err = fmt.Errorf("invalid unit")
		return 0, err
	}

	// check if input is larger than max supported duration (approx. 290y)
	// if it is, set to max possible duration
	var duration time.Duration
	if num > int64(maxDuration/factor) {
		duration = maxDuration
	} else {
		duration = time.Duration(num) * factor
	}

	if duration < 0 {
		return 0, err
	}

	return duration, nil
}

// Kick attempts to kick the user specified user from the server the command was invoked in.
// Fields:
//
//	user: 	User
//	reason: string
func (d *Discord) Kick(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// Mute attempts to mute the user specified user from the server the command was invoked in.
// Fields:
//
//	user: 		User
//	duration:	string
//	reason:		string
func (d *Discord) Mute(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// Unmute attempts to unmute the user specified user from the server the command was invoked in.
// Fields:
//
//	user: 		User
//	reason:		string
func (d *Discord) Unmute(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// Ban attempts to ban the user specified user from the server the command was invoked in.
// Fields:
//
//	user:		User
//	reason:		string
func (d *Discord) Ban(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// Unban attempts to unban the user specified user from the server the command was invoked in.
// Fields:
//
//	user:		User
//	reason:		string
func (d *Discord) Unban(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// RemoveNickname attempts to remove the currently set nickname on the specified user
// in the server the command was invoked in.
// Fields:
//
//	user:		User
//	reason:		string
func (d *Discord) RemoveNickname(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// SetNickname attempts to set the nickname of the specified user in the server
// the command was invoked in.
// Fields:
//
//	user:		User
//	nickname:	string
//	reason:		string
func (d *Discord) SetNickname(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// Slowmode attempts to set the current channel to slowmode.
// Fields:
//
//	duration:	string
func (d *Discord) Slowmode(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// SlowmodeOff attempts to remove slowmode from the current channel.
func (d *Discord) SlowmodeOff(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// Purge attempts to remove the last message-number messages from the specified channel.
// Fields:
//
//	channel:		Channel
//	message-number:		integer
func (d *Discord) Purge(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// Exile attempts to add the exile role to the user, effectively soft-banning them.
// Fields:
//
//	user:		User
//	duration:	string
//	reason:		string
func (d *Discord) Exile(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// Unexile attempts to remove the exile role from the user.
// Fields:
//
//	user:		User
//	reason:		string
func (d *Discord) Unexile(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// SetModLoggingChannel sets the specified channel to the moderation log channel
// All logged commands will be logged to this channel.
// Fields:
//
//	channel:	Channel
func (d *Discord) SetModLoggingChannel(s *discordgo.Session, i *discordgo.InteractionCreate) {
	options := i.ApplicationCommandData().Options
	channelID := options[0].ChannelValue(nil).ID
	d.ModLoggingChannelID = channelID

	tempstr := fmt.Sprintf("Mod logging channel set to: <#%v>", channelID)

	err := StartInteraction(s, i.Interaction, tempstr)
	if err != nil {
		fmt.Printf("Unable to send ephemeral message: %v\n", err)
	}
	fmt.Printf("Set the moderation logging channel to: %v\n", channelID)
}

// Warn attempts to warn a user.
// fields:
//
//	user:		User
//	reason:		string
func (d *Discord) Warn(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// ClearWarnings attempts to clear all warnings for a user.
// fields:
//
//	user:		User
func (d *Discord) ClearWarnings(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// DeleteWarning attempts to delete a warning a user.
// fields:
//
//	warning_id:	integer
func (d *Discord) DeleteWarning(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// ShowAllWarnings attempts to show all warnings for a user.
// fields:
//
//	user:		User
func (d *Discord) ShowAllWarnings(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}
