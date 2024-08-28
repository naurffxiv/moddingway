package discord

import (
	"fmt"
	"log"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/naurffxiv/moddingway/internal/database"
	"github.com/naurffxiv/moddingway/internal/enum"
)



// Mute attempts to mute the user specified user from the server the command was invoked in.
// Fields:
//
//	user: 		User
//	duration:	string
//	reason:		string
func (d *Discord) Mute(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

// Unmute attempts to unmute the user specified user from the server the command was invoked in.
// Fields:
//
//	user: 		User
//	reason:		string
func (d *Discord) Unmute(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

// Ban attempts to ban the user specified user from the server the command was invoked in.
// Fields:
//
//	user:		User
//	reason:		string
func (d *Discord) Ban(s *discordgo.Session, i *discordgo.InteractionCreate) {
	optionMap := mapOptions(i)
	logMsg, _ := d.LogCommand(i.Interaction)

	state := &InteractionState{
		session:     s,
		interaction: i,
		logMsg:      logMsg,
		isFirst:     true,
	}

	userToBan := optionMap["user"].UserValue(nil).ID

	// Check if user exists in guild
	_, err := d.GetUserInGuild(state.interaction.GuildID, userToBan)
	if err != nil {
		tempstr := fmt.Sprintf("Could not ban user <@%v>", userToBan)
		log.Printf("%v: %v\n", tempstr, err)

		err = RespondToInteraction(state.session, state.interaction.Interaction, tempstr, &state.isFirst)
		if err != nil {
			log.Printf("Unable to send ephemeral message: %v\n", err)
		}

		return
	}

	// DM the user regarding the ban
	banstr := fmt.Sprintf(
		"You are being banned from `%v` for the following reason:\n> %v\nYou are able to appeal this ban through the link provided: https://dyno.gg/form/33b5a650",
		GuildName,
		optionMap["reason"].StringValue(),
	)
	_ = d.SendDMToUser(state, userToBan, banstr)

	// Attempt to ban user
	if len(optionMap["reason"].StringValue()) > 0 {
		err = d.Session.GuildBanCreateWithReason(i.GuildID, userToBan, optionMap["reason"].StringValue(), 0)
		if err != nil {
			tempstr := fmt.Sprintf("Unable to ban user <@%v>", userToBan)
			log.Printf("%v: %v\n", tempstr, err)
			RespondAndAppendLog(state, tempstr)
			d.EditLogMsg(logMsg)
			return
		}
		tempstr := fmt.Sprintf("<@%v> has been banned", userToBan)
		RespondAndAppendLog(state, tempstr)
		d.EditLogMsg(logMsg)
	} else {
		err = RespondToInteraction(s, i.Interaction, "Please provide a reason for the ban.", &state.isFirst)
		if err != nil {
			log.Printf("Unable to send ephemeral message: %v\n", err)
		}

		return
	}
}

// Unban attempts to unban the user specified user from the server the command was invoked in.
// Fields:
//
//	user:		User
//	reason:		string
func (d *Discord) Unban(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

// RemoveNickname attempts to remove the currently set nickname on the specified user
// in the server the command was invoked in.
// Fields:
//
//	user:		User
//	reason:		string
func (d *Discord) RemoveNickname(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

// SetNickname attempts to set the nickname of the specified user in the server
// the command was invoked in.
// Fields:
//
//	user:		User
//	nickname:	string
//	reason:		string
func (d *Discord) SetNickname(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

// Purge attempts to remove the last message-number messages from the specified channel.
// Fields:
//
//	channel:		Channel
//	message-number:		integer
func (d *Discord) Purge(s *discordgo.Session, i *discordgo.InteractionCreate) {

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
		_ = d.SendDMToUser(state, userToExile.ID, tempstr)
		d.EditLogMsg(logMsg)

		defer d.EditLogMsg(logMsg)

		dbUserID, err := database.GetUser(d.Conn, userToExile.ID, i.GuildID)
		if err != nil {
			log.Println("User not found in database, adding user...")
			dbUserID, err = database.AddUser(d.Conn, userToExile.ID, i.GuildID)
			if err != nil {
				tempstr = fmt.Sprintf("Unable to add user <@%v> to the database", userToExile.ID)
				log.Printf("%v: %v\n", tempstr, err)
				RespondAndAppendLog(state, tempstr)
				return
			}
		}

		exileEntryArgs := database.AddExileEntryArgs{
			DbUserID:    dbUserID,
			Reason:      optionMap["reason"].StringValue(),
			ExileStatus: enum.TimedExile,
			StartTime:   startTime.UTC().Format(time.RFC3339),
			EndTime:     endTime.UTC().Format(time.RFC3339),
		}
		exileID, err := database.AddExileEntryTimed(d.Conn, exileEntryArgs)
		if err != nil {
			tempstr = "Unable to add entry to the database"
			log.Printf("%v: %v\n", tempstr, err)
			RespondAndAppendLog(state, tempstr)
			return
		}

		logMsg.Embeds[0].Footer = &discordgo.MessageEmbedFooter{Text: fmt.Sprintf("Exile ID: %v", exileID)}

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
		_ = d.SendDMToUser(state, userToExile.ID, tempstr)

		defer d.EditLogMsg(logMsg)

		dbUserID, err := database.GetUser(d.Conn, userToExile.ID, i.GuildID)
		if err != nil {
			log.Println("User not found in database, adding user...")
			dbUserID, err = database.AddUser(d.Conn, userToExile.ID, i.GuildID)
			if err != nil {
				tempstr = fmt.Sprintf("Unable to add user <@%v> to the database", userToExile.ID)
				log.Printf("%v: %v\n", tempstr, err)
				RespondAndAppendLog(state, tempstr)
				return
			}
		}

		exileEntryArgs := database.AddExileEntryArgs{
			DbUserID:    dbUserID,
			Reason:      optionMap["reason"].StringValue(),
			ExileStatus: enum.IndefiniteExile,
			StartTime:   startTime.UTC().Format(time.RFC3339),
		}
		exileID, err := database.AddExileEntryIndefinite(d.Conn, exileEntryArgs)
		if err != nil {
			RespondAndAppendLog(state, "Unable to add entry to the database")
			return
		}
		logMsg.Embeds[0].Footer = &discordgo.MessageEmbedFooter{Text: fmt.Sprintf("Exile ID: %v", exileID)}

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
	err := d.UnexileUser(state, exiledUser.ID)
	if err != nil {
		return
	}
	// DM user regarding the unexile, doesn't matter if DM fails
	tempstr := fmt.Sprintf("You have been unexiled from `%v`.",
		GuildName,
	)
	_ = d.SendDMToUser(state, exiledUser.ID, tempstr)

	defer d.EditLogMsg(state.logMsg)

	dbUserID, err := database.GetUser(d.Conn, exiledUser.ID, i.GuildID)
	if err != nil {
		RespondAndAppendLog(state, "Unable to get user from database")
		return
	}

	exileID, err := database.GetUserExile(d.Conn, dbUserID)
	if err != nil {
		RespondAndAppendLog(state, "Unable to get user's most recent exile")
		return
	}
	logMsg.Embeds[0].Footer = &discordgo.MessageEmbedFooter{Text: fmt.Sprintf("Exile ID: %v", exileID)}

	err = database.RemoveExileEntry(d.Conn, exileID)
	if err != nil {
		tempstr := fmt.Sprintf("Unable to remove exile ID %v", exileID)
		log.Printf("%v: %v\n", tempstr, err)
		RespondAndAppendLog(state, tempstr)
		return
	}
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

	logMsg, _ := d.LogCommand(i.Interaction)
	state := &InteractionState{
		session:     s,
		interaction: i,
		logMsg:      logMsg,
		isFirst:     true,
	}

	tempstr := fmt.Sprintf("Mod logging channel set to: <#%v>", channelID)
	RespondAndAppendLog(state, tempstr)
	d.EditLogMsg(logMsg)

	err := StartInteraction(s, i.Interaction, tempstr)
	if err != nil {
		log.Printf("Unable to send ephemeral message: %v\n", err)
	}
	log.Printf("Set the moderation logging channel to: %v\n", channelID)
}

// Strike attempts to give a user a strike.
// fields:
//
//	user:		User
//	reason:		string
func (d *Discord) Strike(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

// ClearStrikes attempts to clear all strikes for a user.
// fields:
//
//	user:		User
func (d *Discord) ClearStrikes(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

// DeleteStrike attempts to delete a strike from a user.
// fields:
//
//	warning_id:	integer
func (d *Discord) DeleteStrike(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

// ShowAllStrikes attempts to show all strikes for a user.
// fields:
//
//	user:		User
func (d *Discord) ShowAllStrikes(s *discordgo.Session, i *discordgo.InteractionCreate) {

}
