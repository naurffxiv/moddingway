from discord.ext.commands import Bot
from .autounexile import autounexile_users


def start_tasks(self):
    autounexile_users.start(self)
