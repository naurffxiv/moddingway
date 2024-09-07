package discord

func (d *Discord) TempSendDMToUser(userID string, message string) error {
	channel, err := d.Session.UserChannelCreate(userID)
	if err != nil {
		return err
	} else {
		_, err = d.Session.ChannelMessageSend(channel.ID, message)
		return err
	}
}