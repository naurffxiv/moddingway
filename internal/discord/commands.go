package discord

import (
	"fmt"

	"github.com/bwmarrin/discordgo"
)

func (d *Discord) Kick(s *discordgo.Session, i *discordgo.InteractionCreate) {
	options := i.ApplicationCommandData().Options
	optionMap := make(map[string]*discordgo.ApplicationCommandInteractionDataOption, len(options))
	for _, opt := range options {
		optionMap[opt.Name] = opt
	}

	userToKick := optionMap["user"].UserValue(nil).ID

	var err error
	if optionMap["reason"] != nil {
		err = d.Session.GuildMemberDeleteWithReason(i.GuildID, userToKick, optionMap["reason"].StringValue())
	} else {
		err = d.Session.GuildMemberDelete(i.GuildID, userToKick)
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

func (d *Discord) Mute(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

func (d *Discord) Unmute(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

func (d *Discord) Ban(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

func (d *Discord) Unban(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

func (d *Discord) RemoveNickname(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

func (d *Discord) SetNickname(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

func (d *Discord) Slowmode(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

func (d *Discord) SlowmodeOff(s *discordgo.Session, i *discordgo.InteractionCreate) {

}

func (d *Discord) Purge(s *discordgo.Session, i *discordgo.InteractionCreate) {

}
