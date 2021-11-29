import requests
import json
import datetime
import sys
from dateutil.parser import parse as to_datetime
try:
    import pandas as pd
except:
    pass

from pyteamup.utils.utilities import *
from pyteamup.utils.constants import *
from pyteamup.Event import Event
from pyteamup.Key import Key


class Calendar:
    def __init__(self, cal_id, api_key):
        self.__calendar_id = cal_id
        self.__api_key = api_key
        self.__cal_base = f'/{cal_id}'
        self.__token_str = f'?_teamup_token={self.api_key}'
        self.__headers = {'Content-type': 'application/json', 'Teamup-Token': self.__api_key}
        self.__subcalendars = None
        self.__valid_api = None
        self.__configuration = None
        self.__keys = None

        self._base_url = BASE_URL + self.__cal_base
        self._event_collection_url = self._base_url + EVENTS_BASE
        self._subcalendars_url = self._base_url + SUBCALENDARS_BASE
        self._check_access_url = BASE_URL + CHECK_ACCESS_BASE
        self._accesskey_url = self._base_url + KEYS_BASE

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
            req = requests.get(self._check_access_url, headers=self.__headers)
            try:
                check_status_code(self._check_access_url, req.status_code, self.__headers)
                self.__valid_api = True
            except HTTPError as e:
                self.__valid_api = False
            return self.__valid_api
        else:
            return self.__valid_api

    @property
    def keys(self):
        self.__keys = self.get_key_collection()
        return self.__keys

    @property
    def configuration(self):
        if self.__configuration is None:
            print('Fetching configuration')
            url = self._base_url + CONFIGURATION_BASE
            req = requests.get(url, headers=self.__headers)
            check_status_code(url, req.status_code, headers=self.__headers)
            self.__configuration = json.loads(req.text)['configuration']
        return self.__configuration

    @property
    def subcalendars(self):
        if not self.__subcalendars:
            print('Fetching Subcalendars')
            req = requests.get(self._subcalendars_url, headers=self.__headers)
            check_status_code(self._subcalendars_url, req.status_code, self.__headers)
            self.__subcalendars = json.loads(req.text)['subcalendars']
        return self.__subcalendars

    def clear_calendar_cache(self):
        self.__subcalendars = None
        self.__configuration = None

    def get_event_collection(self, start_dt=None, end_dt=None, subcal_id=None, returnas='events', markdown=False):
        """
        Method allows bulk fetching of events that fall between the provided time frame. If None is provided then
        the current date -30 and +180 days is used.

        :param start_dt: if set as None then set as today minus 30 days
        :param end_dt:  if left as None then set as today plus 180 days
        :param subcal_id: optional str or list-like if a different calendar should be queried
        :return: json of events
        """
        if returnas not in ('events', 'dataframe', 'dict'):
            raise ValueError('Returnas not recognized. Recognized values: event, series, dict')

        if start_dt is None:
            start_dt = datetime.date.today() - datetime.timedelta(30)
        if end_dt is None:
            end_dt = datetime.date.today() + datetime.timedelta(180)

        subcal_par = ''
        if subcal_id:
            if isinstance(subcal_id, (list, tuple)):
                for id in subcal_id:
                    subcal_par += f'&subcalendarId[]={id}'
            else:
                subcal_par = f'&subcalendarId[]={subcal_id}'

        if markdown == True:
            para_markdown = '&format[]=markdown'
        else:
            para_markdown = ''
            
        parameters = f'&startDate={start_dt.strftime("%Y-%m-%d")}&endDate={end_dt.strftime("%Y-%m-%d")}' + subcal_par + para_markdown
        url = self._event_collection_url + parameters
        req = requests.get(url, headers=self.__headers)
        check_status_code(url, req.status_code, self.__headers)
        self.events_json = json.loads(req.text)['events']

        if returnas == 'events':
            return [Event(self, **event_dict) for event_dict in self.events_json]
        elif returnas == 'dataframe' and 'pandas' in sys.modules:
            return pd.DataFrame.from_records(self.events_json)
        else:
            return self.events_json

    def _create_event_from_json(self, payload):
        """ Lazy Creation of Event by passing a formatted payload"""
        resp = requests.post(self._event_collection_url, data=payload, headers=self.__headers)
        try:
            check_status_code(self._event_collection_url, resp.status_code, self.__headers)
        except:
            print(payload)
            print(resp.text)
            raise
        return resp.text

    def get_event(self, event_id, returnas='event'):
        if returnas not in ('event', 'series', 'dict'):
            raise ValueError('Returnas not recognized. Recognized values: event, series, dict')

        url = self._base_url + EVENTS_BASE + f'/{event_id}'
        resp = requests.get(url, headers=self.__headers)
        check_status_code(url, resp.status_code, headers=self.__headers)
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

    def get_changed_events(self, modified_since, returnas='event'):
        """
        Get changed events since given unix time
        :param modified_since: <int> Unix timestamp, must be less than 30 days old
        :param returnas: <str> `event` `series` `dict` are valid options
        :return: Tuple of event list and returned timestamp
        """
        if returnas not in ('event', 'series', 'dict'):
            raise ValueError('Returnas not recognized. Recognized values: event, series, dict')
        url = self._base_url + EVENTS_BASE + '&modifiedSince=' + str(modified_since)
        resp = requests.get(url, headers=self.__headers)
        check_status_code(url, resp.status_code, headers=self.__headers)
        events_json = json.loads(resp.text)['events']
        timestamp = json.loads(resp.text)['timestamp']

        if returnas == 'events':
            return [Event(self, **event_dict) for event_dict in events_json], timestamp
        elif returnas == 'dataframe' and 'pandas' in sys.modules:
            return pd.DataFrame.from_records(events_json), timestamp
        else:
            return events_json, timestamp

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
                start_dt = to_datetime(start_dt)
                end_dt = to_datetime(end_dt)
            except:
                raise ValueError('Parse failed, please pass all dates as a datetime object')
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

    def get_key_collection(self, returnas='key'):
        # GET /{calendarKey}/keys
        if returnas not in ('key', 'dict'):
            raise ValueError('Return as must be one of: "key", "dict" ')
        req = requests.get(self._accesskey_url, headers=self.__headers)
        check_status_code(self._accesskey_url, req.status_code, headers=self.__headers)
        keys = json.loads(req.text)
        if returnas == 'key':
            return (Key(calendar=self, **key) for key in keys['keys'])
        return tuple(keys['keys'])


    def get_key(self, key_id, returnas='key'):
        # Returns a key for the calendar
        # GET /{calendarKey}/keys/{keyId}
        if returnas not in ('key', 'dict'):
            raise ValueError('Return as must be one of: key, dict')

        url = self._accesskey_url + f'/{key_id}'
        req = requests.get(url, headers=self.__headers)
        check_status_code(url, req.status_code, headers=self.__headers)
        keys_json = json.loads(req.text)
        if returnas == 'key':
            return Key(calendar=self, **keys_json['key'])

        return self.keys_json['key']

    def create_key(self, key_name, key_share_type, key_perms, key_active=True, key_admin=False, key_require_pass=False,
                   key_pass="", key_all_other=None):
        # Creates a new key for the calendar
        # POST /{calendarKey}/keys
        if isinstance(key_name, str) == False:
            raise Exception('Key name must be a string')

        payload = {
            "name": key_name,
            "active": key_active,
            "admin": key_admin,
        }

        if isinstance(key_require_pass, bool) == False:
            raise Exception('Key require_pass must be a boolean')
        if key_require_pass == True:
            # user wants to add a password
            payload['require_password'] = key_require_pass
            if isinstance(key_pass, str) == False:
                raise Exception('Key pass must be a string')
            if key_pass == "":
                raise Exception('Key password cannot be empty')
            payload['password'] = key_pass
        else:
            # user does not want to add a password
            payload['require_password'] = key_require_pass
            payload['password'] = ""

        if key_share_type not in self.share_types:
            raise Exception(f'Invalid share type: {key_share_type}')
        if key_share_type == 'all_subcalendars':
            if key_perms not in self.permissions:
                raise Exception(f'Invalid permission: {key_perms}')
            # All subcalendars have the same permissions
            payload['share_type'] = key_share_type
            payload['role'] = key_perms
        elif key_share_type == 'selected_subcalendars':
            if not isinstance(key_perms, dict):
                raise Exception(f'Invalid key_perms: {key_perms}')
            payload['share_type'] = key_share_type
            payload['subcalendar_permissions'] = {}
            if key_all_other != None:
                # Set all other subcalendars to specified permission
                if key_all_other not in self.permissions:
                    raise Exception(f'Invalid key_perms: {key_perms}')
                subcalendar = Calendar(self.__calendar_id, self.__api_key).subcalendars
                for subcal in subcalendar:
                    payload['subcalendar_permissions'][str(subcal['id'])] = key_all_other
                payload['role'] = key_all_other
            for perm in key_perms:
                # Overwrite all other perm with specified perm
                if key_perms[perm] not in self.permissions:
                    raise Exception(f'Invalid key_perms: {key_perms}')
                payload['subcalendar_permissions'][perm] = key_perms[perm]

        payloadjson = json.dumps(payload)
        req = requests.post(self.url, headers=self._json_headers, data=payloadjson)
        check_status_code(req.status_code)
        self.keys_json = json.loads(req.text)
        return self.keys_json['key']

    def find_key_by_name(self, key_name, case_sensitive=False, exact_match=False):
        # Finds a key by name
        # GET /{calendarKey}/keys
        keys = self.keys
        find = []
        for key in keys:
            if case_sensitive == True:
                if exact_match == True:
                    # Ex=T | Cs=T
                    if key_name == key.name:
                        find.append(key)
                else:
                    # Ex=F | Cs=T
                    if key_name in key.name:
                        find.append(key)
            else:
                if exact_match == True:
                    # Ex=T | Cs=F
                    if key_name.lower() == key.name.lower():
                        find.append(key)
                else:
                    # Ex=T | Cs=F
                    if key_name.lower() in key.name.lower():
                        find.append(key)

        if len(find) == 0:
            raise Exception(f'Key {key_name} not found')
        if len(find) == 1:
            return find[0]
        return find

    def find_key_by_perm(self):
        # Find keys with specific permissions
        # GET /{calendarKey}/keys
        raise NotImplementedError

    def find_key_by_date(self):
        # Find keys created in time frame.
        # GET /{calendarKey}/keys
        raise NotImplementedError

    def delete_key(self, key_id):
        # Deletes a key for the calendar
        # DELETE /{calendarKey}/keys/{keyId}
        if isinstance(key_id, int) == False:
            raise TypeError('Key id must be an integer')

        url = self._accesskey_url + f'/{str(key_id)}'
        req = requests.delete(url, headers=self.__headers)
        check_status_code(url, req.status_code, headers=self.__headers)
        return True
