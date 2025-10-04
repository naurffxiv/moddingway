from .autounexile import autounexile_users
from .forum_automod import autodelete_threads
from .strike_decrement import decrement_strikes


def start_tasks(self):
    autounexile_users.start(self)
    autodelete_threads.start(self)
    # autodelete_event_threads.start(self)
    decrement_strikes.start(self)
