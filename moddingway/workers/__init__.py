from .autounexile import autounexile_users
from .forum_automod import autodelete_threads, autodelete_posts
from .strike_decrement import decrement_strikes


def start_tasks(self):
    autounexile_users.start(self)
    autodelete_threads.start(self)
    decrement_strikes.start(self)
    autodelete_posts.start(self)
