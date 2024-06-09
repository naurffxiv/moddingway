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
	exileRole := d.Roles[i.GuildID]["Exiled"]
	verifiedRole := d.Roles[i.GuildID]["Verified"]
	logMsg, err := d.LogCommand(i.Interaction)
	if err != nil {
		fmt.Printf("Failed to log: %v\n", err)
	}

	state := &InteractionState{
		session:     s,
		interaction: i,
		logMsg:      logMsg,
		isFirst:     true,
	}

	// Calculate duration of exile
	startTime := time.Now()
	duration, err := parseDuration(optionMap["duration"].StringValue())
	if err != nil {
		fmt.Printf("Failed to parse duration: %v\n", err)
		return
	}

	userToExile := optionMap["user"].UserValue(nil)

	// Check if user meets the requirements for an exile
	memberToExile := d.ExileCheckUserHelper(state, userToExile.ID)
	if memberToExile == nil {
		return
	}

	// Exile the user
	// Remove Verified role
	err = s.GuildMemberRoleRemove(i.GuildID, userToExile.ID, verifiedRole.ID)
	if err != nil {
		tempstr := fmt.Sprintf("Could not remove role %v from user <@%v>", verifiedRole.Name, userToExile.ID)
		fmt.Printf("%v: %v\n", tempstr, err)
		RespondToInteraction(s, i.Interaction, tempstr, &state.isFirst)

		logMsg.Embeds[0].Description += fmt.Sprintf("\n%v", tempstr)
		_, err = d.Session.ChannelMessageEditEmbed(d.ModLoggingChannelID, logMsg.ID, logMsg.Embeds[0])
		if err != nil {
			fmt.Printf("Unable to edit log message: %v\n", err)
		}
		return
	}
	// Add exiled role
	err = s.GuildMemberRoleAdd(i.GuildID, userToExile.ID, exileRole.ID)
	if err != nil {
		tempstr := fmt.Sprintf("Could not give user <@%v> role %v", userToExile.ID, exileRole.Name)
		fmt.Printf("%v: %v\n", tempstr, err)
		RespondToInteraction(s, i.Interaction, tempstr, &state.isFirst)

		logMsg.Embeds[0].Description += fmt.Sprintf("\n%v", tempstr)
		_, err = d.Session.ChannelMessageEditEmbed(d.ModLoggingChannelID, logMsg.ID, logMsg.Embeds[0])
		if err != nil {
			fmt.Printf("Unable to edit log message: %v\n", err)
		}
		return
	}

	// Inform invoker and edit log message of successful exile
	endTime := startTime.Add(duration)
	tempstr := fmt.Sprintf(
		"\nUser <@%v> has been exiled until <t:%v>",
		userToExile.ID,
		endTime.Unix(),
	)
	logMsg.Embeds[0].Description += tempstr
	RespondToInteraction(s, i.Interaction, tempstr, &state.isFirst)

	// DM user regarding the exile
	channel, err := s.UserChannelCreate(userToExile.ID)
	if err != nil {
		tempstr := fmt.Sprintf("Could not create a DM with user %v", userToExile.ID)
		fmt.Printf("%v: %v\n", tempstr, err)
		RespondToInteraction(s, i.Interaction, tempstr, &state.isFirst)
		logMsg.Embeds[0].Description += "\nFailed to notify of the exile via DM"
	} else {
		tempstr := fmt.Sprintf("You are being exiled from `%v` until <t:%v> for the following reason:\n> %v",
			GuildName,
			endTime.Unix(),
			optionMap["reason"].StringValue(),
		)
		_, err = s.ChannelMessageSend(channel.ID, tempstr)
		if err != nil {
			tempstr := fmt.Sprintf("Could not send a DM to user <@%v>", userToExile.ID)
			fmt.Printf("%v: %v\n", tempstr, err)
			RespondToInteraction(s, i.Interaction, tempstr, &state.isFirst)
			logMsg.Embeds[0].Description += "\nFailed to notify of the exile via DM"
		}
	}

	// Edit embed with end-result
	_, err = d.Session.ChannelMessageEditEmbed(d.ModLoggingChannelID, logMsg.ID, logMsg.Embeds[0])
	if err != nil {
		fmt.Printf("Unable to edit log message: %v\n", err)
	}

	time.Sleep(duration)

	logMsg.Embeds[0].Description = fmt.Sprintf("Exile duration for <@%v> is over", userToExile.ID)

	// Unexile user
	err = s.GuildMemberRoleRemove(i.GuildID, userToExile.ID, exileRole.ID)
	// Abort adding verified role if removing exiled role failed
	if err != nil {
		tempstr := fmt.Sprintf("Could not remove role %v from user <@%v>", exileRole.Name, userToExile.ID)
		fmt.Printf("%v: %v\n", tempstr, err)
		logMsg.Embeds[0].Description += fmt.Sprintf("\n%v", tempstr)
	} else {
		// Re-add verified role to user
		err = s.GuildMemberRoleAdd(i.GuildID, userToExile.ID, verifiedRole.ID)
		if err != nil {
			tempstr := fmt.Sprintf("Could not give user <@%v> role %v", userToExile.ID, verifiedRole.ID)
			fmt.Printf("%v: %v\n", tempstr, err)
			logMsg.Embeds[0].Description += tempstr
		} else {
			tempstr := fmt.Sprintf("\nUser <@%v> has been successfully unexiled", userToExile.ID)
			logMsg.Embeds[0].Description += tempstr
		}
	}

	// Send follow-up log message
	logMsg.Embeds[0].Timestamp = time.Now().Format(time.RFC3339)
	_, err = d.Session.ChannelMessageSendEmbed(
		d.ModLoggingChannelID,
		logMsg.Embeds[0],
	)
	if err != nil {
		fmt.Printf("Failed to log: %v\n", err)
	}
}

// Unexile attempts to remove the exile role from the user.
// Fields:
//
//	user:		User
//	reason:		string
func (d *Discord) Unexile(s *discordgo.Session, i *discordgo.InteractionCreate) {
	isFirst := true
	optionMap := mapOptions(i)
	exileRole := d.Roles[i.GuildID]["Exiled"]
	verifiedRole := d.Roles[i.GuildID]["Verified"]
	logMsg, err := d.LogCommand(i.Interaction)
	if err != nil {
		fmt.Printf("Failed to log: %v\n", err)
	}

	exiledUser := optionMap["user"].UserValue(nil)

	// Check if user exists in guild
	exiledMember, err := d.GetUserInGuild(i.GuildID, exiledUser.ID)
	if err != nil {
		tempstr := fmt.Sprintf("Could not find user <@%v> in guild", exiledUser.ID)
		fmt.Printf("%v: %v\n", tempstr, err)
		RespondToInteraction(s, i.Interaction, tempstr, &isFirst)
		return
	}

	// Check if user has specified roles
	isExiled := false
	isVerified := false
	for _, role := range exiledMember.Roles {
		if role == exileRole.ID {
			isExiled = true
		} else if role == verifiedRole.ID {
			isVerified = true
		}
	}

	if !isExiled {
		tempstr := fmt.Sprintf("User <@%v> is not currently exiled, nothing has been done", exiledUser.ID)
		RespondToInteraction(s, i.Interaction, tempstr, &isFirst)
		logMsg.Embeds[0].Description += fmt.Sprintf("\n%v", tempstr)
		_, err = d.Session.ChannelMessageEditEmbed(d.ModLoggingChannelID, logMsg.ID, logMsg.Embeds[0])
		if err != nil {
			fmt.Printf("Unable to edit log message: %v\n", err)
		}
		return
	}

	if isVerified {
		tempstr := fmt.Sprintf("User <@%v> is both exiled and verified, nothing has been done", exiledUser.ID)
		RespondToInteraction(s, i.Interaction, tempstr, &isFirst)
		logMsg.Embeds[0].Description += fmt.Sprintf("\n%v", tempstr)
		_, err = d.Session.ChannelMessageEditEmbed(d.ModLoggingChannelID, logMsg.ID, logMsg.Embeds[0])
		if err != nil {
			fmt.Printf("Unable to edit log message: %v\n", err)
		}
		return
	}

	// Attempt to remove role from user
	err = s.GuildMemberRoleRemove(i.GuildID, exiledUser.ID, exileRole.ID)
	// Abort adding verified role if removing exiled role failed
	if err != nil {
		tempstr := fmt.Sprintf("Could not remove role %v from user <@%v>", exileRole.Name, exiledUser.ID)
		fmt.Printf("%v: %v\n", tempstr, err)
		logMsg.Embeds[0].Description += fmt.Sprintf("\n%v", tempstr)
	} else {
		// Re-add verified role to user
		err = s.GuildMemberRoleAdd(i.GuildID, exiledUser.ID, verifiedRole.ID)
		if err != nil {
			tempstr := fmt.Sprintf("Could not give user <@%v> role %v", exiledUser.ID, verifiedRole.ID)
			fmt.Printf("%v: %v\n", tempstr, err)
			RespondToInteraction(s, i.Interaction, tempstr, &isFirst)
			logMsg.Embeds[0].Description += fmt.Sprintf("\n%v", tempstr)
		} else {
			tempstr := fmt.Sprintf("User <@%v> has been successfully unexiled", exiledUser.ID)
			RespondToInteraction(s, i.Interaction, tempstr, &isFirst)
			logMsg.Embeds[0].Description += fmt.Sprintf("\n%v", tempstr)
		}
	}

	// Update log message of status
	_, err = d.Session.ChannelMessageEditEmbed(d.ModLoggingChannelID, logMsg.ID, logMsg.Embeds[0])
	if err != nil {
		fmt.Printf("Unable to edit log message: %v\n", err)
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
