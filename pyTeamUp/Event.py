""" Placeholder for Event Class that will eventually hold """
from warnings import warn
class Event:
    def __init(self, id, remote_id=None, series_id=None,subcalendar_ids=None,
               start_dt=None, end_dt=None, all_day=None, title=None, who=None, location=None, notes=None,
               rrule=None, ristart_dt=None, rsstart_dt=None, tz=None, version=None, readonly=None, duration=None,
               signup_enabled=None, signup_deadline=None, signup_visibility=None, signup_limit=None, comments_enabled=None,
               comments_visibility=None, custom=None, creation_dt=None, update_dt=None, delete_dt=None):
        self.id = id
        self.remote_id = remote_id
        self.series_id = series_id
        self.subcalendar_ids = subcalendar_ids
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.all_day = all_day
        self.title = title
        self.who = who
        self.location = location
        self.notes = notes
        self.rrule = rrule
        self.ristart_dt = ristart_dt
        self.rsstart_dt = rsstart_dt
        self.tz = tz
        self.version = version
        self.readonly = readonly
        #self.duration = duration
        #self.signup_enabled = signup_enabled
        #self.signup_deadline = signup_deadline
        #self.signup_visibility = signup_visibility
        #self.signup_limit = signup_limit
        #self.comments_enabled = comments_enabled
        #self.comments_visibility = comments_visibility
        #self.custom = custom
        self.creation_dt = creation_dt
        self.update_dt = update_dt
        self.delete_dt = delete_dt

    @property
    def subcalendar_ids(self):
        return self.__subcalendar_ids

    @subcalendar_ids.setter
    def subcalendar_ids(self, ids):
        warn('Not Currently Connected to the API, no changes have been made to the event on Teamup')
        if not isinstance(ids, (int, str, list, tuple)):
            raise TypeError(f'Invalid type for ids. Supplied type: {type(ids)}')
        # ADD API EXECUTION HERE
        self.__subcalendar_ids = ids





