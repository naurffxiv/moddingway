from .autounexile import autounexile_users
from .forum_automod import autodelete_threads


def start_tasks(self):
    autounexile_users.start(self)
    autodelete_threads.start(self)
