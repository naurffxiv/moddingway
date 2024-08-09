package main

import (
	"fmt"

	"github.com/bwmarrin/discordgo"
	"github.com/naurffxiv/moddingway/internal/database"
	"github.com/naurffxiv/moddingway/internal/discord"
	"github.com/naurffxiv/moddingway/internal/enum"
)

func autoUnexile(d *discord.Discord) {
	pendingUnexiles, err := database.GetPendingUnexiles(d.Conn)
	if err != nil {
		tempstr := "Unable to get pending unexiles"
		fmt.Printf("%v\n", tempstr)
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

	// send the embed before returning in any branch of code
	// return value and error not needed
	defer func() {
		_, _ = d.SendEmbed(d.ModLoggingChannelID, logMsg)
	}()

	// Check if user is in guild
	member, err := d.Session.GuildMember(pending.DiscordGuildID, pending.DiscordUserID)
	if err != nil {
		tempstr := fmt.Sprintf("Could not find user <@%v> in guild", pending.DiscordUserID)
		printAndAppend(logMsg, tempstr, err)
		removeExileEntryWrapper(d, logMsg, pending.ExileID)
		return
	}

	// make log message look pretty
	logMsg.Author = &discordgo.MessageEmbedAuthor{
		Name: member.User.Username,
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

	logMsg.Description += "Successfully unexiled user\n"
	removeExileEntryWrapper(d, logMsg, pending.ExileID)
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
		fmt.Printf("%v\n", str)
	} else {
		fmt.Printf("%v: %v\n", str, err)
	}
	logMsg.Description += fmt.Sprintf("%v\n", str)
}