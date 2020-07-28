import datetime
from pytz import timezone


class Meta:
    current_date: datetime.datetime

    def __init__(self):
        utc = timezone("UTC")
        self.current_date = datetime.datetime.now(tz=utc)
