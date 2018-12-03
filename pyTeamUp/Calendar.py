import requests
import json
import datetime
import sys
try:
    import pandas as pd
except:
    from pyteamup.utils.pandas.datetimes import to_datetime

from pyteamup.utils.utilities import *
from pyteamup.utils.constants import *
from pyteamup.event import Event

class Calendar:
    def __init__(self, cal_id, api_key):
        self.__calendar_id = cal_id
        self.__api_key = api_key
        self.__cal_base = f'/{cal_id}'
        self.__token_str = f'?_teamup_token={self.api_key}'
        self.__subcalendars = None
        self.__valid_api = None
        self.__configuration = None

        self._base_url = BASE_URL + self.__cal_base
        self._event_collection_url = self._base_url + EVENTS_BASE + self.__token_str
        self._subcalendars_url = self._base_url + SUBCALENDARS_BASE + self.__token_str
        self._check_access_url = BASE_URL + CHECK_ACCESS_BASE + self.__token_str

        self.events_json = None

        if not self.valid_api:
            raise Exception(f'Invalid Api Key: {self.api_key}')

    def __str__(self):
        return self.calendar_id

    @property
    def api_key(self):
        return self.__api_key

    @property
    def calendar_id(self):
        return self.__calendar_id

    @property
    def valid_api(self):
        """Makes a request to the calendar to see if the api is valid"""
        if not self.__valid_api:
            req = requests.get(self._check_access_url)
            try:
                check_status_code(req.status_code)
                self.__valid_api = True
            except:
                self.__valid_api = False
            return self.__valid_api

        else:
            return None

    @property
    def configuration(self):
        if self.__configuration is None:
            print('Fetching configuration')
            req = requests.get(self._base_url + CONFIGURATION_BASE + self.__token_str)
            check_status_code(req.status_code)
            self.__configuration = json.loads(req.text)['configuration']
        return self.__configuration

    @property
    def subcalendars(self):
        if not self.__subcalendars:
            print('Fetching Subcalendars')
            req = requests.get(self._subcalendars_url)
            check_status_code(req.status_code)
            self.__subcalendars = json.loads(req.text)['subcalendars']
        return self.__subcalendars

    def clear_calendar_cache(self):
        self.__subcalendars = None
        self.__configuration = None

    def get_event_collection(self, start_date=None, end_date=None, subcal_id=None, returnas='events'):
        """
        Method allows bulk fetching of events that fall between the provided time frame. If None is provided then
        the current date -30 and +180 days is used.

        :param start_date: if set as None then set as today minus 30 days
        :param end_date:  if left as None then set as today plus 180 days
        :param subcal_id: optional str or list-like if a different calendar should be queried
        :return: json of events
        """
        if returnas not in ('events', 'dataframe', 'dict'):
            raise TypeError('Returnas not recognized. Recognized values: event, series, dict')

        if start_date is None:
            start_date = datetime.date.today() - datetime.timedelta(30)
        if end_date is None:
            end_date = datetime.date.today() + datetime.timedelta(180)

        subcal_par = ''
        if subcal_id:
            if isinstance(subcal_id, (list, tuple)):
                for id in subcal_id:
                    subcal_par += f'&subcalendarId[]={id}'
            else:
                subcal_par = f'&subcalendarId[]={subcal_id}'

        parameters = f'&startDate={start_date.strftime("%Y-%m-%d")}&endDate={end_date.strftime("%Y-%m-%d")}' + subcal_par
        req = requests.get(self._event_collection_url + parameters)
        check_status_code(req.status_code)
        self.events_json = json.loads(req.text)['events']

        if returnas == 'events':
            return [Event(self, **event_dict) for event_dict in self.events_json]
        elif returnas == 'dataframe' and 'pandas' in sys.modules:
            return pd.DataFrame.from_records(self.events_json)
        else:
            return self.events_json

    def _create_event_from_json(self, payload):
        """ Lazy Creation of Event by passing a formatted payload"""
        resp = requests.post(self._event_collection_url, data=payload, headers=POST_HEADERS)
        try:
            check_status_code(resp.status_code)
        except:
            print(payload)
            print(resp.text)
            raise
        return resp.text

    def get_event(self, event_id, returnas='event'):
        if returnas not in ('event', 'series', 'dict'):
            raise TypeError('Returnas not recognized. Recognized values: event, series, dict')

        url = self._base_url + EVENTS_BASE + f'/{event_id}' + self.__token_str
        resp = requests.get(url)
        check_status_code(resp.status_code)
        event_dict = json.loads(resp.text)['event']
        if returnas == 'event':
            return Event(self, **event_dict)
        elif returnas == 'series' and 'pandas' in sys.modules:
            return pd.Series(event_dict)
        else:
            return event_dict

    def get_subcalendar(self):
        raise NotImplementedError

    def search_events(self):
        raise NotImplementedError

    def get_changed_events(self):
        raise NotImplementedError

    def new_event(self, title, start_dt, end_dt, subcalendar_ids, all_day=False,
                  notes=None, location=None, who=None, remote_id=None, returnas='event'):
        """
        Create a new event within a provided subcalendar. Can return as Event object, Series object, or Dictionary.

        Undo_id not included with return unless returnas='event' in which case it is included with the returned Event Object

        :param subcalendar_id: <str, int, or list-like> Required - the ID of the subcalendar within the calendar the event should be created in.
        :param title: <str> Title of the event, must be
        :param start_dt: <datetime> Start Datetime
        :param end_dt: <datetime> End Datetime
        :param all_day: <Bool> Allday or Not
        :param notes: <str> HTML or Markdown formatted string detailing the Description
        :param location: <str> Location of the event
        :param who: <str>
        :param remote_id: <str> Remote ID of the event, used to link the TeamUp event record to its source information
        :param returnas: <str> `event` `series` `dict` are valid options
        :return:
        """
        if returnas not in ('event','dict','series'):
            raise ValueError(f'Unrecognized returnas paramter: {returnas}')
        if not isinstance(start_dt, datetime.datetime) or not isinstance(end_dt, datetime.datetime):
            try:
                start_dt = pd.to_datetime(start_dt)
                end_dt = pd.to_datetime(end_dt)
            except:
                raise ValueError('All dates must be passed as a datetime object')
        if isinstance(subcalendar_ids, (str, int)):
            subcalendar_ids = [subcalendar_ids]
        if not isinstance(subcalendar_ids, (tuple, list)):
            raise ValueError(f'Unrecognized Type: Subcalendar_ids type: {type(subcalendar_ids)}')

        dict = {'remote_id': remote_id,
                'title': title,
                'subcalendar_ids': subcalendar_ids,
                'start_dt': format_date(start_dt),
                'end_dt': format_date(end_dt),
                'all_day': all_day,
                'notes': notes,
                'location': location,
                'who': who
                }

        resp_text = self._create_event_from_json(json.dumps(dict))
        resp_dict = json.loads(resp_text)
        event_dict = resp_dict['event']
        undo_id = resp_dict['undo_id']

        if returnas == 'event':
            return Event(self, undo_id = undo_id, **event_dict)
        elif returnas == 'series' and 'pandas' in sys.modules:
            return pd.Series(event_dict)
        else:
            return event_dict