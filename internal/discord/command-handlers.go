package discord

import (
	"errors"
	"fmt"
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
			AddStrikeCommand,
			ClearStrikesCommand,
			DeleteStrikeCommand,
			ShowAllStrikesCommand,
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

// CheckUserInGuild checks if the user is in the specified server.
func (d *Discord) CheckUserInGuild(guild_id string, user string) error {
	_, err := d.Session.GuildMember(guild_id, user)
	if err != nil {
		return err
	}
	return nil
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

var AddStrikeCommand = &discordgo.ApplicationCommand{
	Name:                     "strike",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Notify the specified user of the strike being issued.",
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

var ClearStrikesCommand = &discordgo.ApplicationCommand{
	Name:                     "clearstrikes",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Clear all strikes for a specified user.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "User being cleared of warnings",
			Required:    true,
		},
	},
}

var DeleteStrikeCommand = &discordgo.ApplicationCommand{
	Name:                     "deletestrike",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Delete a strike.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionInteger,
			Name:        "strike_id",
			Description: "Strike to be deleted",
			Required:    true,
		},
	},
}

var ShowAllStrikesCommand = &discordgo.ApplicationCommand{
	Name:                     "strikes",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Show all strikes for a specified user.",
	Options: []*discordgo.ApplicationCommandOption{
		{
			Type:        discordgo.ApplicationCommandOptionUser,
			Name:        "user",
			Description: "Specified user's strikes being shown",
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
	case "strike":
		d.Strike(s, i)
	case "clearstrikes":
		d.ClearStrikes(s, i)
	case "deletestrike":
		d.DeleteStrike(s, i)
	case "strikes":
		d.ShowAllStrikes(s, i)
	}
}
