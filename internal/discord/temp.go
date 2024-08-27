package discord

import (
	"fmt"
	"slices"
	"time"

	"github.com/bwmarrin/discordgo"
)

// Functions/methods that are meant to replace the existing non-temp versions during refactoring

func (d *Discord) tempRoleRemoveAddHelper(userID string, guildID string, roleToRemove string, roleToAdd string) error {
	roleIDToRemove := d.Roles[guildID][roleToRemove].ID
	roleIDToAdd := d.Roles[guildID][roleToAdd].ID

	err := d.Session.GuildMemberRoleRemove(guildID, userID, roleIDToRemove)
	if err != nil {
		return err
	} else {
		err = d.Session.GuildMemberRoleAdd(guildID, userID, roleIDToAdd)
		if err != nil {
			return err
		}
	}
	return nil
}

func (d *Discord) tempCheckRoleHelper(guildID string, presentRoles map[string]bool, roleName string, shouldHaveRole bool) error {
	var err error = nil
	roleID := d.Roles[guildID][roleName].ID
	if presentRoles[roleName] != shouldHaveRole {
		if shouldHaveRole {
			err = fmt.Errorf("role not present: %v", roleID)
		} else {
			err = fmt.Errorf("role present: %v", roleID)
		}
	}
	return err
}

func (d *Discord) tempCheckUserForRoles(userID string, guildID string, shouldHave []string, shouldNotHave []string) error {
	member, err := d.Session.GuildMember(guildID, userID)
	if err != nil {
		return err
	}
	presentRoles := d.checkRoleMapHelper(member, slices.Concat(shouldHave, shouldNotHave))

	// check for roles which user should have
	for _, roleName := range shouldHave {
		err = d.tempCheckRoleHelper(guildID, presentRoles, roleName, true)
		if err != nil {
			return err
		}
	}

	// check for roles which user should not have
	for _, roleName := range shouldNotHave {
		err = d.tempCheckRoleHelper(guildID, presentRoles, roleName, false)
		if err != nil {
			return err
		}
	}
	return nil
}

func (d *Discord) TempUnexileUser(userID string, guildID string) error {
	// Check user for specified roles
	roleToRemove := ExiledRole
	roleToAdd := VerifiedRole
	err := d.tempCheckUserForRoles(userID, guildID, []string{roleToRemove}, []string{roleToAdd})
	if err != nil {
		return err
	}

	return d.tempRoleRemoveAddHelper(userID, guildID, roleToRemove, roleToAdd)

}

func CreateMemberEmbed(member *discordgo.Member, description string, footer string) *discordgo.MessageEmbed {
	if member == nil {
		return &discordgo.MessageEmbed{
			Description: description,
			Footer: &discordgo.MessageEmbedFooter{
				Text: footer,
			},
			Timestamp: time.Now().Format(time.RFC3339),
		}
	} else {
		return &discordgo.MessageEmbed{
			Author: &discordgo.MessageEmbedAuthor{
				Name:    member.User.Username,
				IconURL: member.AvatarURL(""),
			},
			Description: description,
			Footer: &discordgo.MessageEmbedFooter{
				Text: footer,
			},
			Timestamp: time.Now().Format(time.RFC3339),
		}
	}
}

func (d *Discord) TempSendDMToUser(userID string, message string) error {
	// Open DM channel with user
	channel, err := d.Session.UserChannelCreate(userID)
	if err != nil {
		return err
	} else {
		_, err = d.Session.ChannelMessageSend(channel.ID, message)
		return err
	}
}