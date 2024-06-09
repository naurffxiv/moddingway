package discord

import (
	"errors"
	"fmt"
	"regexp"
	"strconv"
	"time"

	"github.com/bwmarrin/discordgo"
	"golang.org/x/text/cases"
	"golang.org/x/text/language"
)

// Set up vars for the DefaultMemberPermissions field in each command definition
var (
	adminPermission int64 = discordgo.PermissionAdministrator
)

// AddCommands registers the slash commands with Discord
func (d *Discord) AddCommands(s *discordgo.Session, event *discordgo.Ready) {
	fmt.Printf("Initializing Discord...\n")

	for _, discordGuild := range event.Guilds {

		// Adding commands to a list to prepare in bulk
		var commands []*discordgo.ApplicationCommand
		commands = append(commands,
			KickCommand,
			MuteCommand,
			UnmuteCommand,
			BanCommand,
			UnbanCommand,
			RemoveNicknameCommand,
			SetNicknameCommand,
			SlowmodeCommand,
			SlowmodeOffCommand,
			PurgeCommand,
			ExileCommand,
			UnexileCommand,
			SetModLoggingCommand,
			AddWarningCommand,
			ClearWarningsCommand,
			DeleteWarningCommand,
			ShowAllWarningsCommand,
		)

		fmt.Printf("Adding commands...\n")
		commandList, err := s.ApplicationCommandBulkOverwrite(event.User.ID, discordGuild.ID, commands)
		fmt.Printf("List of successfully created commands:\n")
		for _, command := range commandList {
			fmt.Printf("\t%v\n", command.Name)
		}
		if err != nil {
			fmt.Printf("Could not add some commands: %v \n", err)
		}
	}
}

// GetUserInGuild returns the user in the server
func (d *Discord) GetUserInGuild(guild_id string, user string) (*discordgo.Member, error) {
	member, err := d.Session.GuildMember(guild_id, user)
	if err != nil {
		return nil, err
	}
	return member, nil
}

// LogCommand logs the moderation command in the channel specified by LogChannelID
// It sends an embed with all command arguments as separate fields
// It additionally returns the sent message in case any edits need to be made
func (d *Discord) LogCommand(i *discordgo.Interaction) (*discordgo.Message, error) {
	if len(d.ModLoggingChannelID) == 0 {
		return nil, errors.New("log channel not set")
	}
	options := i.ApplicationCommandData().Options

	// Format embed fields
	var embedFields []*discordgo.MessageEmbedField
	// Action field
	embedFields = append(embedFields, &discordgo.MessageEmbedField{
		Name:  "Action",
		Value: fmt.Sprintf("/%v", i.ApplicationCommandData().Name),
	})
	// Options fields
	for _, opt := range options {
		// Format value based on what type the field is
		var optValue string
		switch opt.Type {
		case discordgo.ApplicationCommandOptionString:
			optValue = opt.StringValue()
		case discordgo.ApplicationCommandOptionInteger:
			optValue = fmt.Sprintf("%v", opt.IntValue())
		case discordgo.ApplicationCommandOptionBoolean:
			optValue = fmt.Sprintf("%t", opt.BoolValue())
		case discordgo.ApplicationCommandOptionUser:
			userID := opt.UserValue(nil).ID
			optValue = fmt.Sprintf("<@%v>", userID)
		case discordgo.ApplicationCommandOptionChannel:
			optValue = fmt.Sprintf("<#%v>", opt.ChannelValue(nil).ID)
		case discordgo.ApplicationCommandOptionNumber:
			optValue = fmt.Sprintf("%v", opt.FloatValue())
		}

		embedFields = append(embedFields, &discordgo.MessageEmbedField{
			Name:  cases.Title(language.English).String(opt.Name),
			Value: optValue,
		})
	}

	actionDescription := fmt.Sprintf("Used `%v` command in <#%v>",
		i.ApplicationCommandData().Name,
		i.ChannelID,
	)

	// Send the embed
	return d.Session.ChannelMessageSendEmbed(
		d.ModLoggingChannelID,
		&discordgo.MessageEmbed{
			Author: &discordgo.MessageEmbedAuthor{
				Name:    i.Member.User.Username,
				IconURL: i.Member.AvatarURL(""),
			},
			Description: actionDescription,
			Fields:      embedFields,
			Timestamp:   time.Now().Format(time.RFC3339),
		},
	)
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

// mapOptions is a helper function that creates a map out of the arguments used in the slash command
func mapOptions(i *discordgo.InteractionCreate) map[string]*discordgo.ApplicationCommandInteractionDataOption {
	options := i.ApplicationCommandData().Options
	optionMap := make(map[string]*discordgo.ApplicationCommandInteractionDataOption, len(options))
	for _, opt := range options {
		optionMap[opt.Name] = opt
	}
	return optionMap
}

var KickCommand = &discordgo.ApplicationCommand{
	Name:                     "kick",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Kick the specified user and notify the user why via DMs.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "User being kicked",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "reason",
			Description: "Reason for kick",
			Required:    true,
		},
	},
}

var MuteCommand = &discordgo.ApplicationCommand{
	Name:                     "mute",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Mute the specified user.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "User being muted",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "duration",
			Description: "Duration of mute (e.g \"1m, 1h, 1d\")",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "reason",
			Description: "Reason for mute",
			Required:    true,
		},
	},
}

var UnmuteCommand = &discordgo.ApplicationCommand{
	Name:                     "unmute",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Unmute the specified user.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "User being unmuted",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "reason",
			Description: "Reason for unmute",
			Required:    true,
		},
	},
}

var BanCommand = &discordgo.ApplicationCommand{
	Name:                     "ban",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Ban the specified user and notify the user why via DMs.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "User being banned",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "reason",
			Description: "Reason for ban",
			Required:    true,
		},
	},
}

var UnbanCommand = &discordgo.ApplicationCommand{
	Name:                     "unban",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Unban the specified user.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "User being unbanned (Discord ID)",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "reason",
			Description: "Reason for unban",
			Required:    true,
		},
	},
}

var RemoveNicknameCommand = &discordgo.ApplicationCommand{
	Name:                     "removenickname",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Remove the nickname of the specified user.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "User whose nickname to remove",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "reason",
			Description: "Reason for nickname removal",
			Required:    true,
		},
	},
}

var SetNicknameCommand = &discordgo.ApplicationCommand{
	Name:                     "setnickname",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Change the nickname of the specified user.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "User whose nickname to rename",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "nickname",
			Description: "Nickname to rename user to",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "reason",
			Description: "Reason for nickname change",
			Required:    true,
		},
	},
}

var SlowmodeCommand = &discordgo.ApplicationCommand{
	Name:                     "slowmode",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Add slowmode to current channel.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "duration",
			Description: "Duration of slowmode (e.g \"1m, 1h, 1d\")",
			Required:    true,
		},
	},
}

var SlowmodeOffCommand = &discordgo.ApplicationCommand{
	Name:                     "slowmodeoff",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Remove slowmode from current channel.",
}

var PurgeCommand = &discordgo.ApplicationCommand{
	Name:                     "purge",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Delete a number of messages from a channel.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionChannel,
			Name:        "channel",
			Description: "Channel to purge",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionInteger,
			Name:        "message-number",
			Description: "Number of messages to purge (100 max)",
			MaxValue:    100,
			Required:    true,
		},
	},
}

var ExileCommand = &discordgo.ApplicationCommand{
	Name:                     "exile",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Exile the specified user.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "User being exiled",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "duration",
			Description: "Duration of exile (e.g \"1m, 1h, 1d\")",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "reason",
			Description: "Reason for exile",
			Required:    true,
		},
	},
}

var UnexileCommand = &discordgo.ApplicationCommand{
	Name:                     "unexile",
	DefaultMemberPermissions: &adminPermission,
	Description:              "unexile the specified user.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "User being unexiled",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "reason",
			Description: "Reason for unexile",
			Required:    true,
		},
	},
}

var SetModLoggingCommand = &discordgo.ApplicationCommand{
	Name:                     "setmodloggingchannel",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Set the log channel for moderation commands.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionChannel,
			Name:        "channel",
			Description: "Channel to log moderation actions in",
			Required:    true,
		},
	},
}

var AddWarningCommand = &discordgo.ApplicationCommand{
	Name:                     "warn",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Warn the specified user.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "User being warned",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "reason",
			Description: "Reason for warning",
			Required:    true,
		},
	},
}

var ClearWarningsCommand = &discordgo.ApplicationCommand{
	Name:                     "clearwarnings",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Clear all warnings for a specified user.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "User being cleared of warnings",
			Required:    true,
		},
	},
}

var DeleteWarningCommand = &discordgo.ApplicationCommand{
	Name:                     "deletewarning",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Delete a warning.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionInteger,
			Name:        "warning_id",
			Description: "Warning to be deleted",
			Required:    true,
		},
	},
}

var ShowAllWarningsCommand = &discordgo.ApplicationCommand{
	Name:                     "warnings",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Show all warnings for a specified user.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "Target user's warnings being shown",
			Required:    true,
		},
	},
}

// InteractionCreate executes the respective function based on what
// slash command was used
func (d *Discord) InteractionCreate(s *discordgo.Session, i *discordgo.InteractionCreate) {
	switch i.ApplicationCommandData().Name {
	case "kick":
		d.Kick(s, i)
	case "mute":
		d.Mute(s, i)
	case "ban":
		d.Ban(s, i)
	case "unban":
		d.Unban(s, i)
	case "removenickname":
		d.RemoveNickname(s, i)
	case "setnickname":
		d.SetNickname(s, i)
	case "slowmode":
		d.Slowmode(s, i)
	case "slowmodeoff":
		d.SlowmodeOff(s, i)
	case "purge":
		d.Purge(s, i)
	case "exile":
		d.Exile(s, i)
	case "unexile":
		d.Unexile(s, i)
	case "setmodloggingchannel":
		d.SetModLoggingChannel(s, i)
	case "warn":
		d.Warn(s, i)
	case "clearwarnings":
		d.ClearWarnings(s, i)
	case "deletewarning":
		d.DeleteWarning(s, i)
	case "warnings":
		d.ShowAllWarnings(s, i)
	}
}
