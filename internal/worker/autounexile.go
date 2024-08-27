package worker

import (
	"fmt"
	"log"

	"github.com/bwmarrin/discordgo"
	"github.com/naurffxiv/moddingway/internal/database"
	"github.com/naurffxiv/moddingway/internal/discord"
	"github.com/naurffxiv/moddingway/internal/enum"
)

func AutoUnexile(d *discord.Discord) {
	pendingUnexiles, err := database.GetPendingUnexiles(d.Conn)
	if err != nil {
		tempstr := "Unable to get pending unexiles"
		log.Printf("%v\n", tempstr)
		return
	}

	for _, pending := range pendingUnexiles {
		processPendingUnexile(d, pending)
	}
}

// processPendingUnexile processes each expired timed exile.
// makes use of defer to send the log message at the end, instead of editing it continuously
func processPendingUnexile(d *discord.Discord, pending database.PendingUnexile) {
	// logging
	description := fmt.Sprintf("<@%v>'s exile has timed out\n", pending.DiscordUserID)
	footer := fmt.Sprintf("Exile ID: %v", pending.ExileID)
	logMsg := discord.CreateMemberEmbed(nil, description, footer)

	// remove exile entry and send the embed before returning in any branch of code
	// return value and error not needed
	defer func() {
		removeExileEntryWrapper(d, logMsg, pending.ExileID)
		_, _ = d.SendEmbed(d.ModLoggingChannelID, logMsg)
	}()

	// Check if user is in guild
	member, err := d.Session.GuildMember(pending.DiscordGuildID, pending.DiscordUserID)
	if err != nil {
		tempstr := fmt.Sprintf("Could not find user <@%v> in guild", pending.DiscordUserID)
		printAndAppend(logMsg, tempstr, err)
		return
	}

	// make log message look pretty
	logMsg.Author = &discordgo.MessageEmbedAuthor{
		Name:    member.User.Username,
		IconURL: member.AvatarURL(""),
	}

	// unexile the user
	err = d.TempUnexileUser(pending.DiscordUserID, pending.DiscordGuildID)
	if err != nil {
		tempstr := fmt.Sprintf("Unable to unexile user <@%v>", pending.DiscordUserID)
		printAndAppend(logMsg, tempstr, err)
		updateExileStatusWrapper(d, logMsg, pending.ExileID, enum.Unknown)
		return
	}

	// send DM to user regarding unexile
	message := fmt.Sprintf("You have been unexiled from %v.", discord.GuildName)
	err = d.TempSendDMToUser(pending.DiscordUserID, message)
	if err != nil {
		tempstr := fmt.Sprintf("Unable to send DM to user regarding unexile: %v", err)
		printAndAppend(logMsg, tempstr, err)
	}

	logMsg.Description += "Successfully unexiled user\n"
}

func updateExileStatusWrapper(d *discord.Discord, logMsg *discordgo.MessageEmbed, exileID int, exileStatus enum.ExileStatus) {
	err := database.UpdateExileStatus(d.Conn, exileID, exileStatus)
	if err != nil {
		tempstr := fmt.Sprintf("Unable to update database for exile ID %v to %v", exileID, exileStatus)
		printAndAppend(logMsg, tempstr, err)
	}
}

func removeExileEntryWrapper(d *discord.Discord, logMsg *discordgo.MessageEmbed, exileID int) {
	err := database.RemoveExileEntry(d.Conn, exileID)
	if err != nil {
		tempstr := fmt.Sprintf("Unable to remove exile ID %v", exileID)
		printAndAppend(logMsg, tempstr, err)
	}
}

func printAndAppend(logMsg *discordgo.MessageEmbed, str string, err error) {
	if err == nil {
		log.Printf("%v\n", str)
	} else {
		log.Printf("%v: %v\n", str, err)
	}
	logMsg.Description += fmt.Sprintf("%v\n", str)
}
