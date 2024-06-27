package discord

import (
	"fmt"
	"time"

	"github.com/bwmarrin/discordgo"
)

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
	optionMap := mapOptions(i)
	logMsg, _ := d.LogCommand(i.Interaction)

	state := &InteractionState{
		session:     s,
		interaction: i,
		logMsg:      logMsg,
		isFirst:     true,
	}

	var duration time.Duration
	var err error

	// Calculate duration of exile if argument is not empty
	startTime := time.Now()
	durationArg, hasDuration := optionMap["duration"]
	if hasDuration {
		duration, err = CalculateDuration(state, startTime, durationArg.StringValue())
		if err != nil {
			return
		}
	}

	userToExile := optionMap["user"].UserValue(nil)

	err = d.ExileUser(state, userToExile.ID, optionMap["reason"].StringValue())
	if err != nil {
		return
	}

	if hasDuration {
		// Inform invoker and edit log message of successful exile
		endTime := startTime.Add(duration)
		tempstr := fmt.Sprintf(
			"User <@%v> has been exiled until <t:%v>",
			userToExile.ID,
			endTime.Unix(),
		)
		RespondAndAppendLog(state, tempstr)

		// DM user regarding the exile, doesn't matter if DM fails
		tempstr = fmt.Sprintf("You are being exiled from `%v` until <t:%v> for the following reason:\n> %v",
			GuildName,
			endTime.Unix(),
			optionMap["reason"].StringValue(),
		)
		d.SendDMToUser(state, userToExile.ID, tempstr)
		d.EditLogMsg(logMsg)

		time.Sleep(duration)

		// Reuse the original embed format but clear existing info
		ClearEmbedDescription(logMsg)
		AppendLogMsgDescription(logMsg, fmt.Sprintf("Exile duration for <@%v> is over", userToExile.ID))
		UpdateLogMsgTimestamp(logMsg)
		if logMsg != nil {
			d.SendEmbed(d.ModLoggingChannelID, logMsg.Embeds[0])
		}

		// Unexile user
		reason := "Exile duration has finished."
		err = d.UnexileUser(state, userToExile.ID, reason)
		if err != nil {
			return
		}
		// DM user regarding the unexile, doesn't matter if DM fails
		tempstr = fmt.Sprintf("You have been unexiled from `%v` for the following reason:\n> %v",
			GuildName,
			reason,
		)
		d.SendDMToUser(state, userToExile.ID, tempstr)
		d.EditLogMsg(state.logMsg)
	} else {
		tempstr := fmt.Sprintf(
			"User <@%v> has been exiled indefinitely",
			userToExile.ID,
		)
		RespondAndAppendLog(state, tempstr)

		// DM user regarding the exile, doesn't matter if DM fails
		tempstr = fmt.Sprintf("You are being exiled from `%v` indefinitely for the following reason:\n> %v",
			GuildName,
			optionMap["reason"].StringValue(),
		)
		d.SendDMToUser(state, userToExile.ID, tempstr)
		d.EditLogMsg(logMsg)
	}
}

// Unexile attempts to remove the exile role from the user.
// Fields:
//
//	user:		User
//	reason:		string
func (d *Discord) Unexile(s *discordgo.Session, i *discordgo.InteractionCreate) {
	optionMap := mapOptions(i)
	logMsg, _ := d.LogCommand(i.Interaction)

	state := &InteractionState{
		session:     s,
		interaction: i,
		logMsg:      logMsg,
		isFirst:     true,
	}

	exiledUser := optionMap["user"].UserValue(nil)

	// Unexile user
	err := d.UnexileUser(state, exiledUser.ID, optionMap["reason"].StringValue())
	if err != nil {
		return
	}
	// DM user regarding the unexile, doesn't matter if DM fails
	tempstr := fmt.Sprintf("You have been unexiled from `%v` for the following reason:\n> %v",
		GuildName,
		optionMap["reason"].StringValue(),
	)
	d.SendDMToUser(state, exiledUser.ID, tempstr)
	d.EditLogMsg(state.logMsg)
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

// Strike attempts to give a user a strike.
// fields:
//
//	user:		User
//	reason:		string
func (d *Discord) Strike(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// ClearStrikes attempts to clear all strikes for a user.
// fields:
//
//	user:		User
func (d *Discord) ClearStrikes(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// DeleteStrike attempts to delete a strike from a user.
// fields:
//
//	warning_id:	integer
func (d *Discord) DeleteStrike(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// ShowAllStrikes attempts to show all strikes for a user.
// fields:
//
//	user:		User
func (d *Discord) ShowAllStrikes(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}
