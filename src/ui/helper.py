import discord
from settings import get_settings
from util import EmbedField, create_interaction_embed_context

settings = get_settings()


def create_modal_embed(interaction: discord.Interaction, modalTitle: str, **kwargs):
    fields = [EmbedField("Action", f"{modalTitle} Modal")]
    if kwargs is not None:
        for key, value in kwargs.items():
            match (type(value)):
                case discord.Member:
                    fields.append(EmbedField(key.title(), f"<@{value.id}>"))
                case discord.ChannelType:
                    fields.append(EmbedField(key.title(), f"<#{value}>"))
                case _:
                    fields.append(EmbedField(key.title(), value))

    return create_interaction_embed_context(
        interaction.guild.get_channel(settings.logging_channel_id),
        user=interaction.user,
        timestamp=interaction.created_at,
        description=f"Used `{modalTitle}` action",
        fields=fields,
    )
