package discord

import (
	"fmt"
	"regexp"
	"slices"
	"strconv"
	"strings"
	"time"

	"github.com/bwmarrin/discordgo"
	"golang.org/x/text/cases"
	"golang.org/x/text/language"
)

type InteractionState struct {
	session     *discordgo.Session
	interaction *discordgo.InteractionCreate
	logMsg      *discordgo.Message
	isFirst     bool
}

// Set up vars for the DefaultMemberPermissions field in each command definition
var (
	adminPermission int64 = discordgo.PermissionAdministrator
)

// AddCommands registers the slash commands with Discord
func (d *Discord) AddCommands(s *discordgo.Session, event *discordgo.Ready) {
	fmt.Printf("Initializing Discord...\n")
	foundTargetGuild := false
	for _, discordGuild := range event.Guilds {
		if discordGuild.ID == d.GuildID {
			foundTargetGuild = true
			// Adding commands to a list to prepare in bulk
			var commands []*discordgo.ApplicationCommand
			commands = append(commands,
				// KickCommand,
				// MuteCommand,
				// UnmuteCommand,
				BanCommand,
				// UnbanCommand,
				// RemoveNicknameCommand,
				// SetNicknameCommand,
				// SlowmodeCommand,
				// SlowmodeOffCommand,
				// PurgeCommand,
				ExileCommand,
				UnexileCommand,
				SetModLoggingCommand,
				// AddStrikeCommand,
				// ClearStrikesCommand,
				// DeleteStrikeCommand,
				// ShowAllStrikesCommand,
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

	if !foundTargetGuild {
		d.Session.Close()
		panic("Bot is not present in the specified guild.")
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

func (d *Discord) SendEmbed(channelID string, embed *discordgo.MessageEmbed) (*discordgo.Message, error) {
	msg, err := d.Session.ChannelMessageSendEmbed(channelID, embed)
	if err != nil {
		fmt.Printf("Failed to log: %v\n", err)
		return nil, err
	}
	return msg, nil
}

// LogCommand logs the moderation command in the channel specified by LogChannelID
// It sends an embed with all command arguments as separate fields
// It additionally returns the sent message in case any edits need to be made
func (d *Discord) LogCommand(i *discordgo.Interaction) (*discordgo.Message, error) {
	if len(d.ModLoggingChannelID) == 0 {
		err := fmt.Errorf("log channel not set")
		fmt.Printf("Failed to log: %v\n", err)
		return nil, err
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
	return d.SendEmbed(
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

	// clean user input
	trimmed := strings.ReplaceAll(userInput, " ", "")
	durationStrings := strings.Split(trimmed, ",")

	// for each substring of format [num][letter] (e.g "24h")
	var totalDuration time.Duration = 0
	for _, durationString := range durationStrings {
		// groups[0] is the entire match, following elements are capture groups
		groups := r.FindStringSubmatch(durationString)
		if len(groups) < 2 {
			err := fmt.Errorf("invalid format")
			fmt.Printf("Failed to parse duration: %v\n", err)
			return 0, err
		}
		num, err := strconv.ParseInt(groups[1], 10, 64)
		if err != nil {
			fmt.Printf("Failed to parse duration: %v\n", err)
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
		default:
			err = fmt.Errorf("invalid unit")
			fmt.Printf("Failed to parse duration: %v\n", err)
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
			err = fmt.Errorf("negative duration")
			fmt.Printf("Failed to parse duration: %v\n", err)
			return 0, err
		}

		// likewise, check if the sum is larger than max supported duration
		if duration > (maxDuration - totalDuration) {
			return maxDuration, nil
		}
		totalDuration += duration
	}

	return totalDuration, nil
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

// AppendLogMsgDescription appends an existing logMsg with the specified text
func AppendLogMsgDescription(logMsg *discordgo.Message, s string) {
	if logMsg != nil {
		logMsg.Embeds[0].Description += fmt.Sprintf("\n%v", s)
	}
}

// EditLogMsg sends the updated logMsg to Discord and overwrites the message referred to by logMsg.ID
func (d *Discord) EditLogMsg(logMsg *discordgo.Message) {
	if logMsg != nil {
		_, err := d.Session.ChannelMessageEditEmbed(d.ModLoggingChannelID, logMsg.ID, logMsg.Embeds[0])
		if err != nil {
			fmt.Printf("Unable to edit log message: %v\n", err)
		}
	}
}

// UpdateLogMsgTimestamp updates the timestamp for the embed in a logMsg
func UpdateLogMsgTimestamp(logMsg *discordgo.Message) {
	if logMsg != nil {
		logMsg.Embeds[0].Timestamp = time.Now().Format(time.RFC3339)
	}
}

// RespondAndAppendLog combines both a response and a log message update into one function
func RespondAndAppendLog(state *InteractionState, message string) {
	err := RespondToInteraction(state.session, state.interaction.Interaction, message, &state.isFirst)
	if err != nil {
		fmt.Printf("Unable to respond to interaction: %v\n", err)
	}
	AppendLogMsgDescription(state.logMsg, message)
}

// SendDMToUser sends a DM to the user specified in `userID` with `message` as its contents
func (d *Discord) SendDMToUser(state *InteractionState, userID string, message string) error {
	// Open DM channel with user
	channel, err := state.session.UserChannelCreate(userID)
	if err != nil {
		tempstr := fmt.Sprintf("Could not create a DM with user %v", userID)
		fmt.Printf("%v: %v\n", tempstr, err)
		RespondAndAppendLog(state, tempstr)
		return err
	} else {
		_, err = state.session.ChannelMessageSend(channel.ID, message)
		if err != nil {
			tempstr := fmt.Sprintf("Could not send a DM to user <@%v>", userID)
			fmt.Printf("%v: %v\n", tempstr, err)
			RespondAndAppendLog(state, tempstr)
			return err
		}
		return nil
	}
}

// checkRoleMapHelper takes a member and a slice of rolesToCheck (role names) and returns
// a map of bools (map[roleName] bool) indicating whether or not the role is present
func (d *Discord) checkRoleMapHelper(member *discordgo.Member, rolesToCheck []string) map[string]bool {
	// initialize map
	presentRoles := make(map[string]bool)
	for _, roleToCheck := range rolesToCheck {
		roleID := d.Roles[member.GuildID][roleToCheck].ID
		if slices.Contains(member.Roles, roleID) {
			presentRoles[roleToCheck] = true
		} else {
			presentRoles[roleToCheck] = false
		}

	}

	return presentRoles
}

// checkRoleHelper checks whether a specific role `roleName` is present/not present
// from the map generated by checkRoleMapHelper()
// returns an error if the role's presence is not as expected based on `shouldHaveRole`
func (d *Discord) checkRoleHelper(state *InteractionState, userID string, presentRoles map[string]bool, roleName string, shouldHaveRole bool) error {
	var err error = nil
	roleID := d.Roles[state.interaction.GuildID][roleName].ID
	if presentRoles[roleName] != shouldHaveRole {
		var tempstr string
		if shouldHaveRole {
			tempstr = fmt.Sprintf("User <@%v> does not have role <@&%v>", userID, roleID)
			err = fmt.Errorf("role not present: %v", roleID)
		} else {
			tempstr = fmt.Sprintf("User <@%v> has role <@&%v>", userID, roleID)
			err = fmt.Errorf("role present: %v", roleID)
		}
		RespondAndAppendLog(state, tempstr)
	}
	return err
}

// CheckUserForRoles checks the user for a slice of roles they should or should not have
// returns an error if any specified role fails the check
func (d *Discord) CheckUserForRoles(state *InteractionState, userID string, shouldHave []string, shouldNotHave []string) error {
	// check if user is present in guild
	member, err := d.GetUserHelper(state, userID)
	if err != nil {
		return err
	}
	presentRoles := d.checkRoleMapHelper(member, slices.Concat(shouldHave, shouldNotHave))

	// check for roles which user should have
	for _, roleName := range shouldHave {
		err = d.checkRoleHelper(state, userID, presentRoles, roleName, true)
		if err != nil {
			AppendLogMsgDescription(state.logMsg, "Nothing has been done")
			return err
		}
	}

	// check for roles which user should not have
	for _, roleName := range shouldNotHave {
		err = d.checkRoleHelper(state, userID, presentRoles, roleName, false)
		if err != nil {
			AppendLogMsgDescription(state.logMsg, "Nothing has been done")
			return err
		}
	}
	return nil
}

// GetUserHelper checks whether the user is still in the guild or not
// returns nil if the user does not and returns the member on success
func (d *Discord) GetUserHelper(state *InteractionState, userID string) (*discordgo.Member, error) {
	// Check if user exists in guild
	member, err := d.GetUserInGuild(state.interaction.GuildID, userID)
	if err != nil {
		tempstr := fmt.Sprintf("Could not find user <@%v> in guild", userID)
		fmt.Printf("%v: %v\n", tempstr, err)
		RespondAndAppendLog(state, tempstr)
		return nil, err
	}
	return member, nil
}

func CalculateDuration(state *InteractionState, startTime time.Time, stringDuration string) (time.Duration, error) {
	duration, err := parseDuration(stringDuration)
	if err != nil {
		tempstr := fmt.Sprintf("Could not parse duration: %v\nNothing has been done", err)
		RespondAndAppendLog(state, tempstr)
		return 0, err
	}
	return duration, nil
}

func ClearEmbedDescription(logMsg *discordgo.Message) {
	if logMsg != nil {
		logMsg.Embeds[0].Description = ""
	}
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
			Name:        "reason",
			Description: "Reason for exile",
			Required:    true,
		},
		{
			Type:        discordgo.ApplicationCommandOptionString,
			Name:        "duration",
			Description: "Duration of exile (e.g \"1m, 1h, 1d\")",
			Required:    false,
		},
	},
}

var UnexileCommand = &discordgo.ApplicationCommand{
	Name:                     "unexile",
	DefaultMemberPermissions: &adminPermission,
	Description:              "Unexile the specified user.",
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
	// case "kick":
	// 	d.Kick(s, i)
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
	// case "slowmode":
	// 	d.Slowmode(s, i)
	// case "slowmodeoff":
	// 	d.SlowmodeOff(s, i)
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

// RoleRemoveAddHelper removes a role `roleIDToRemove` and then adds a role `roleIDToAdd` to the user `userID`
func (d *Discord) RoleRemoveAddHelper(state *InteractionState, userID string, roleToRemove string, roleToAdd string) error {
	roleIDToRemove := d.Roles[state.interaction.GuildID][roleToRemove].ID
	roleIDToAdd := d.Roles[state.interaction.GuildID][roleToAdd].ID

	// Attempt to remove role first
	err := state.session.GuildMemberRoleRemove(state.interaction.GuildID, userID, roleIDToRemove)
	if err != nil {
		// Abort entire process if role removal fails
		tempstr := fmt.Sprintf("Could not remove the role <@&%v> from user <@%v>", roleIDToAdd, userID)
		fmt.Printf("%v: %v\n", tempstr, err)
		RespondAndAppendLog(state, tempstr)
		return err
	} else {
		// Otherwise add role
		err = state.session.GuildMemberRoleAdd(state.interaction.GuildID, userID, roleIDToAdd)
		if err != nil {
			tempstr := fmt.Sprintf("Could not give user <@%v> role <@&%v>", userID, roleIDToAdd)
			fmt.Printf("%v: %v\n", tempstr, err)
			RespondAndAppendLog(state, tempstr)
			return err
		} else {
			return nil
		}
	}
}

func (d *Discord) ExileUser(state *InteractionState, userID string, reason string) error {
	// Check user for specified roles
	roleToRemove := VerifiedRole
	roleToAdd := ExiledRole
	err := d.CheckUserForRoles(state, userID, []string{roleToRemove}, []string{roleToAdd})
	if err != nil {
		d.EditLogMsg(state.logMsg)
		fmt.Printf("Unable to exile user <@%v>: %v\n", userID, err)
		return err
	}

	// Remove verified role and add exiled role
	return d.RoleRemoveAddHelper(state, userID, roleToRemove, roleToAdd)
}

func (d *Discord) UnexileUser(state *InteractionState, userID string, reason string) error {
	// Check user for specified roles
	roleToRemove := ExiledRole
	roleToAdd := VerifiedRole
	err := d.CheckUserForRoles(state, userID, []string{roleToRemove}, []string{roleToAdd})
	if err != nil {
		d.EditLogMsg(state.logMsg)
		fmt.Printf("Unable to unexile user <@%v>: %v\n", userID, err)
		return err
	}

	// Remove exile role and add verified role
	err = d.RoleRemoveAddHelper(state, userID, roleToRemove, roleToAdd)
	if err != nil {
		d.EditLogMsg(state.logMsg)
		fmt.Printf("Unable to unexile user <@%v>: %v\n", userID, err)
		return err
	}

	tempstr := fmt.Sprintf("User <@%v> has been successfully unexiled", userID)
	RespondAndAppendLog(state, tempstr)
	return nil
}
