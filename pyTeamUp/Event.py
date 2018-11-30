from warnings import warn
import requests
import json
from datetime import datetime
from collections import OrderedDict
try:
    from pandas import to_datetime
except:
    from pyteamup.utils.pandas.datetimes import to_datetime

from pyteamup.utils.utilities import *
from pyteamup.utils.constants import *

class Event:
    def __init__(self, parent_calendar, id, remote_id=None, series_id=None,subcalendar_ids=None, subcalendar_id=None,
               start_dt=None, end_dt=None, all_day=None, title=None, who=None, location=None, notes=None,
               rrule=None, ristart_dt=None, rsstart_dt=None, tz=None, version=None, readonly=None, duration=None,
               creation_dt=None, update_dt=None, delete_dt=None ,signup_enabled=None, signup_deadline=None,
               signup_visibility=None, signup_limit=None, comments_enabled=None, comments_visibility=None, custom=None,
               surpress_warning=False, undo_id=None):

        self.surpress_warning = surpress_warning
        self.__parent_calendar = parent_calendar
        self.__id = id
        self.__remote_id = remote_id
        self.__series_id = series_id
        self.__subcalendar_ids = subcalendar_ids
        if subcalendar_id:
            if not subcalendar_ids:
                self.__subcalendar_ids = [subcalendar_id]
        self.__start_dt = to_datetime(start_dt)
        self.__end_dt = to_datetime(end_dt)
        self.__all_day = all_day
        self.__title = title
        self.__who = who
        self.__location = location
        self.__notes = notes
        self.__rrule = rrule
        self.__ristart_dt = to_datetime(ristart_dt)
        self.__rsstart_dt = to_datetime(rsstart_dt)
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
        self.__creation_dt = to_datetime(creation_dt)
        self.__update_dt = to_datetime(update_dt)
        self.__delete_dt = to_datetime(delete_dt)
        self.__undo_id = undo_id
        self.__aux = None
        self.__history = None
        self.__deleted = bool(delete_dt)

        self.__batch = False
        self.__batch_update_records = OrderedDict()


        self.__api_key = self.parent_calendar.api_key
        self.__token_str = f'?_teamup_token={self.api_key}'
        self.__url = self.__parent_calendar._base_url + EVENTS_BASE + f'/{self.event_id}'
        self.__api_url = self.__url + self.__token_str

    def __str__(self):
        return self.event_id

    @property
    def event_id(self):
        return self.__id

    @property
    def can_undo(self):
        return bool(self.__undo_id)

    @property
    def deleted(self):
        return self.__deleted

    @property
    def remote_id(self):
        return self.__remote_id

    @remote_id.setter
    def remote_id(self, new_id):
        if new_id != self.remote_id:
            update_dict = {'remote_id': new_id}
            self.execute_update(update_dict)
        else:
            if not self.surpress_warning:
                warn('New Remote Id is identical to current ID. No changes made')

    @property
    def start_dt(self):
        return self.__start_dt

    @start_dt.setter
    def start_dt(self, new_date):
        if not isinstance(new_date, datetime):
            new_date = to_datetime(new_date)

        if new_date != self.start_dt:
            update_dict = {'start_dt': new_date}
            self.execute_update(update_dict)
        else:
            if not self.surpress_warning:
                warn('New Start Date is identical to current. No changes made')

    @property
    def end_dt(self):
        return self.__end_dt

    @end_dt.setter
    def end_dt(self, new_date):
        if not isinstance(new_date, datetime):
            new_date = to_datetime(new_date)
        if new_date != self.end_dt:
            update_dict = {'end_dt': new_date}
            self.execute_update(update_dict)
        else:
            if not self.surpress_warning:
                warn('New End Date is identical to current. No changes made')

    @property
    def duration(self):
        return self.__duration

    @property
    def all_day(self):
        return self.__all_day

    @all_day.setter
    def all_day(self, value):
        if not isinstance(value, bool):
            raise TypeError('Must pass a boolean argument as new value')

        if value != self.all_day:
            update_dict = {'all_day': value}
            self.execute_update(update_dict)
        else:
            if not self.surpress_warning:
                warn('New all_day value is identical to current. No changes made')

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, new_title):
        if new_title != self.title:
            update_dict = {'title': new_title}
            self.execute_update(update_dict)
        else:
            if not self.surpress_warning:
                warn('New title is identical to current. No changes made')

    @property
    def who(self):
        return self.__who

    @who.setter
    def who(self, who):
        if who != self.who:
            update_dict = {'who': who}
            self.execute_update(update_dict)
        else:
            if not self.surpress_warning:
                warn('New location is identical to current. No changes made')

    @property
    def location(self):
        return self.__location

    @location.setter
    def location(self, location):
        if location != self.location:
            update_dict = {'location': location}
            self.execute_update(update_dict)
        else:
            if not self.surpress_warning:
                warn('New location is identical to current. No changes made')
    @property
    def notes(self):
        return self.__notes

    @notes.setter
    def notes(self, description):
        if description != self.notes:
            update_dict = {'notes': description}
            self.execute_update(update_dict)
        else:
            if not self.surpress_warning:
                warn('New description is identical to current. No changes made')

    @property
    def subcalendar_ids(self):
        return self.__subcalendar_ids

    @subcalendar_ids.setter
    def subcalendar_ids(self, ids):
        if isinstance(ids, (str, int)):
            ids = [ids]
        if not isinstance(ids, (list, tuple)):
            raise TypeError(f'Invalid type for ids. Supplied type: {type(ids)}')

        if ids != self.subcalendar_ids:
            update_dict = {'subcalendar_ids': ids}
            self.execute_update(update_dict)
        else:
            if not self.surpress_warning:
                warn('New description is identical to current. No changes made')

    @property
    def rrule(self):
        return self.__rrule

    @property
    def ristart_dt(self):
        return self.__ristart_dt

    @property
    def rsstart_dt(self):
        return self.__rsstart_dt

    @property
    def tz(self):
        return self.__tz

    @property
    def version(self):
        return self.__version

    @property
    def readonly(self):
        return self.__readonly

    @property
    def signup_enabled(self):
        return self.__signup_enabled

    @property
    def signup_deadline(self):
        return self.__signup_deadline

    @property
    def signup_visibility(self):
        return self.__signup_visibility

    @property
    def signup_limit(self):
        return self.__signup_limit

    @property
    def comments_enabled(self):
        return self.__comments_enabled

    @property
    def comments_visibility(self):
        return self.__comments_visibility

    @property
    def custom(self):
        return self.__custom

    @property
    def creation_dt(self):
        return self.__creation_dt

    @property
    def update_dt(self):
        return self.__update_dt

    @property
    def delete_dt(self):
        return self.__delete_dt

    @property
    def series_id(self):
        return self.__series_id

    @property
    def parent_calendar(self):
        return self.__parent_calendar

    @property
    def api_key(self):
        return self.__api_key

    @property
    def url(self):
        return self.__url

    @property
    def api_url(self):
        return self.__api_url

    @property
    def batch(self):
        return self.__batch

    @property
    def aux(self):
        return self.__aux

    @property
    def history(self):
        return self.__history

    @property
    def _update_dict(self):
        return {
            "id": self.event_id,
            "subcalendar_ids": self.subcalendar_ids,
            "start_dt": format_date(self.start_dt),
            "end_dt": format_date(self.end_dt),
            "version": self.version,
            "title": self.title,
            'notes': self.notes,
            'all_day': self.all_day,
            'who': self.who,
            'location': self.location,
            'remote_id': self.remote_id
        }

    def execute_update(self, update_dict):
        """Executes an update. if Batch Mode is enabled then it will store it in the queue until batch execute is called
        at which point batch mode is disabled and the queue passed as one single update.
        :param: update_dict: Required dictionary of update elements. Should conform to the api reference from types and
                            valid fields. Note that custom fields are not supported by the api currently.
        """
        if self.batch:
            if not self.surpress_warning:
                warn('Batch Mode Enabled, Request not sent until Event.batch_submit() called')
            for k, v in update_dict.items():
                self.__batch_update_records[k] = v
            return 'Batch Updated'
        else:
            final_update_dict = self._update_dict
            for k in update_dict:
                val = update_dict[k]
                if isinstance(val, datetime.datetime):
                    val = format_date(val)
                final_update_dict[k] = val
            final_update_json = json.dumps(final_update_dict)
            resp = requests.put(self.api_url, data=final_update_json, headers=POST_HEADERS)
            check_status_code(resp.status_code)
            resp_json = json.loads(resp.text)
            event_data = resp_json['event']
            undo_id = resp_json['undo_id']
            self.__init__(self.__parent_calendar, undo_id=undo_id, **event_data)

    def enable_batch_update(self):
        """Interface for Batch Update mode to turn the mode On. In this mode all changes to the event are cached until
        batch_execute() is called"""
        if not self.batch:
            self.__batch = True
            print('Batch Mode Enabled')
        else:
            if not self.surpress_warning:
                warn('Batch mode already enabled')

    def disable_batch_update(self, clear=False, force=False):
        """Interface for Batch Update Mode to turn the mode off.
        :param: clear: Boolean, used if calling disable manually and wish to discard"""
        if self.batch:
            if self.__batch_update_records:
                if clear:
                    to_disp_len = len(self.__batch_update_records)
                    if not self.surpress_warning:
                        warn(f'Disposing of {to_disp_len} batch updates in queue')
                    self.__batch_update_records = OrderedDict()
                else:
                    if not force:
                        raise Exception('Non-Empty Queue, cannot turn off batch mode. Run batch_commit() or pass clear=True or pass force=True')
                    print('Batch Cache not cleared')
            self.__batch = False
            print('Batch Update Disabled')
        else:
            if not self.surpress_warning:
                warn('Batch mode already enabled')

    def batch_commit(self):
        """
        Interface for Batch Update to call the update. This necessarily turns off batch update, executes the cache, and clears the cache.

        No change is made if batch queue is empty
        :return:
        """
        if self.batch:
            if self.__batch_update_records:
                self.disable_batch_update(force=True)
                self.execute_update(self.__batch_update_records)
                self.__batch_update_records = OrderedDict()
            else:
                if not self.surpress_warning:
                    warn('No Updates in Queue, no changes made, batch mode still enabled.')
        else:
            raise Exception('Batch Mode is not enabled.')

    def delete(self, redit=None):
        """
        Simple method for deleting
        :param subcalendar_id:
        :return:
        """
        if redit:
            if not self.rrule:
                raise AttributeError('rredit parameter included but event is not a recurring event')
            redit_param = f'&redit={redit}'
        else:
            if self.rrule:
                raise AttributeError('Recurring events require rredit paramter passed')
            redit_param = ''

        url = self.api_url + f'&version={self.version}' + redit_param
        resp = requests.delete(url)
        check_status_code(resp.status_code)
        resp_json = json.loads(resp.text)
        self.__undo_id = resp_json['undo_id']
        self.__deleted = True
        if not self.surpress_warning:
            warn('Event Deleted but delete_dt not set until event is refreshed from server. Use Calendar to get the event again')





