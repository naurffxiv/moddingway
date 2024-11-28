class Exile(object):
    def __init__(
        self,
        exile_id,
        user_id,
        discord_id,
        reason,
        exile_status,
        start_timestamp,
        end_timestamp,
    ):
        self.exile_id = exile_id
        self.user_id = user_id
        self.discord_id = discord_id
        self.reason = reason
        self.exile_status = exile_status
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
