class PendingExile(object):
    def __init__(self, exile_id, user_id, end_timestamp):
        self.exile_id = int(exile_id)
        self.user_id = int(user_id)
        self.end_timestamp = end_timestamp
