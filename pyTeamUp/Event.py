""" Placeholder for Event Class that will eventually hold """
from warnings import warn
import requests
import json

from pyteamup.utils.utilities import *
from pyteamup.utils.constants import *

class Event:
    def __init__(self, parent_calendar, id, remote_id=None, series_id=None,subcalendar_ids=None, subcalendar_id=None, #Note that subcalendar_id is deprecated and is not used, merely caught.
               start_dt=None, end_dt=None, all_day=None, title=None, who=None, location=None, notes=None,
               rrule=None, ristart_dt=None, rsstart_dt=None, tz=None, version=None, readonly=None, duration=None,
               creation_dt=None, update_dt=None, delete_dt=None ,signup_enabled=None, signup_deadline=None,
               signup_visibility=None, signup_limit=None, comments_enabled=None, comments_visibility=None, custom=None,
               surpress_warning=True):

        self.surpress_warning = surpress_warning
        self.__parent_calendar = parent_calendar
        self.__id = id
        self.__remote_id = remote_id
        self.__series_id = series_id
        self.__subcalendar_ids = subcalendar_ids
        self.__start_dt = start_dt
        self.__end_dt = end_dt
        self.__all_day = all_day
        self.__title = title
        self.__who = who
        self.__location = location
        self.__notes = notes
        self.__rrule = rrule
        self.__ristart_dt = ristart_dt
        self.__rsstart_dt = rsstart_dt
        self.__tz = tz
        self.__version = version
        self.__readonly = readonly
        self.__duration = duration
        self.__signup_enabled = signup_enabled
        self.__signup_deadline = signup_deadline
        self.__signup_visibility = signup_visibility
        self.__signup_limit = signup_limit
        self.__comments_enabled = comments_enabled
        self.__comments_visibility = comments_visibility
        self.__custom = custom
        self.__creation_dt = creation_dt
        self.__update_dt = update_dt
        self.__delete_dt = delete_dt

        self.__batch = False
        self.__batch_update_records = {}

        self.__aux = None
        self.__history = None
        self.__api_key = self.parent_calendar.api_key
        self.__token_str = f'?_teamup_token={self.api_key}'
        self.__url = self.__parent_calendar._base_url + EVENTS_BASE + f'/{self.event_id}'
        self.__api_url = self.__url + self.__token_str
    
    @property
    def event_id(self):
        return self.__id

    @property
    def remote_id(self):
        return self.__remote_id

    @remote_id.setter
    def remote_id(self, new_id):
        if new_id != self.remote_id:
            raise NotImplementedError('API Not Set to Update')
        else:
            if not self.surpress_warning:
                warn('New Remote Id is identical to current ID. No changes made')



    @property
    def parent_calendar(self):
        return self.__parent_calendar

    @property
    def api_key(self):
        return self.__api_key

    @property
    def url(self):
        return self.__url

    def api_url(self):
        return self.__api_url

    @property
    def batch(self):
        return self.__batch

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

    def execute_update(self, update_dict, surpress_warning=False):
        if self.batch:
            if not surpress_warning:
                warn('Batch Mode Enabled, Request not sent until Event.batch_submit() called')
            for k, v in update_dict.items():
                self.__batch_update_records[k] = v
            return 'Batch Updated'
        else:
            resp = requests.put(self.url, data=json.dumps(update_dict), headers=POST_HEADERS)
            check_status_code(resp.status_code)
            resp_json = json.loads(resp)
            event_data = resp_json['event']
            undo_id = resp_json['undo_id']

    def enable_batch_update(self):
        """Interface for Batch Update mode to turn the mode On. In this mode all changes to the event are cached until
        batch_execute() is called"""
        if not self.batch:
            self.__batch = True
            print('Batch Mode Enabled')
        else:
            warn('Batch mode already enabled')

    def disable_batch_update(self, clear=False):
        """Interface for Batch Update Mode to turn the mode off. If changes are queued up then they will be erased with a warning"""
        if self.batch:
            if self.__batch_update_records:
                if clear:
                    to_disp_len = len(self.__batch_update_records)
                    warn(f'Disposing of {to_disp_len} batch updates in queue')
                else:
                    raise Exception('Non-Empty Queue, cannot turn off batch mode. Run execute_batch() or pass clear=True')
            self.__batch = False
            self.__batch_update_records = {}
        else:
            warn('Batch mode already disabled')

    def batch_update(self):
        if self.batch:
            if self.__batch_update_records:
                resp = requests.put(self.url, data=json.dumps(self.__batch_update_records), headers=POST_HEADERS)
                check_status_code(resp.status_code)
                self.__batch_update_records = {}
                return resp.text
            else:
                warn('No Updates in Queue, no request made')
        else:
            raise Exception('Batch Mode Disabled')






