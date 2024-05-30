package discord

import (
	"fmt"

	"github.com/bwmarrin/discordgo"
)

// Kick attempts to kick the user specified user from the server the command was invoked in.
// Fields:
//
//	user: 	User
//	reason: string
func (d *Discord) Kick(s *discordgo.Session, i *discordgo.InteractionCreate) {
	options := i.ApplicationCommandData().Options
	optionMap := make(map[string]*discordgo.ApplicationCommandInteractionDataOption, len(options))
	for _, opt := range options {
		optionMap[opt.Name] = opt
	}

	userToKick := optionMap["user"].UserValue(nil).ID

	// Check if user exists in guild
	err := d.CheckUserInGuild(i.GuildID, userToKick)
	if err != nil {
		tempstr := fmt.Sprintf("Could not kick user <@%v>", userToKick)
		fmt.Printf("%v: %v\n", tempstr, err)
		StartInteraction(s, i.Interaction, tempstr)
		return
	}

	// DM the user regarding the kick
	channel, err := s.UserChannelCreate(userToKick)
	if err != nil {
		tempstr := fmt.Sprintf("Could not send a DM to user %v", userToKick)
		fmt.Printf("%v: %v\n", tempstr, err)
		// Abort kick if failed to DM?
		//return
		StartInteraction(s, i.Interaction, tempstr)
	} else {
		// Get guild name
		var guildname string
		guild, err := d.Session.Guild(i.GuildID)
		if err != nil {
			fmt.Printf("Unable to find guild name: %v", err)
			guildname = i.GuildID
		} else {
			guildname = guild.Name
		}

		tempstr := fmt.Sprintf("You are being kicked from %v for the reason:\n%v",
			guildname,
			optionMap["reason"].StringValue(),
		)

		_, err = s.ChannelMessageSend(channel.ID, tempstr)
		if err != nil {
			tempstr := fmt.Sprintf("Could not send a DM to user %v", userToKick)
			fmt.Printf("%v: %v\n", tempstr, err)
			// Abort kick if failed to DM?
			//return
			StartInteraction(s, i.Interaction, tempstr)
		}
	}

	// Attempt to kick user
	if len(optionMap["reason"].StringValue()) > 0 {
		err = d.Session.GuildMemberDeleteWithReason(i.GuildID, userToKick, optionMap["reason"].StringValue())
	} else {
		StartInteraction(s, i.Interaction, "Please provide a reason for the kick.")
		return
	}

	if err != nil {
		tempstr := fmt.Sprintf("Could not kick user <@%v>", userToKick)
		fmt.Printf("%v: %v\n", tempstr, err)
		StartInteraction(s, i.Interaction, tempstr)
	} else {
		tempstr := fmt.Sprintf("User <@%v> has been kicked.", userToKick)
		fmt.Printf("%v\n", tempstr)
		StartInteraction(s, i.Interaction, tempstr)
	}

}

// Mute attempts to mute the user specified user from the server the command was invoked in.
// Fields:
//
//	user: 		User
//	duration:	integer
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
//	duration:	integer
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
//	message-number:	integer
func (d *Discord) Purge(s *discordgo.Session, i *discordgo.InteractionCreate) {
	return
}

// Exile attempts to add the exile role to the user, effectively soft-banning them.
// Fields:
//
//	user:		User
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
