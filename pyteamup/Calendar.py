"""
Calendar Object for PyTeamUp package

Author: David Jones
Creation Date: 11/27/2017
Last Updated 12/3/2021
Contributor(s): Frederick Schaller IV (@LogicallyUnfit on Github)

"""
from warnings import warn
import logging
import sys
from dateutil.parser import parse as to_datetime
try:
    import pandas as pd
except:
    pass

from pyteamup.utils.func import *
from pyteamup.utils.const import *
from pyteamup.Event import Event
from pyteamup.Key import Key

logger = logging.getLogger(__name__)

class Calendar:
    def __init__(self, cal_id, api_key, password=None):
        """
        Primary Controller of an individual TeamUp Calendar. Uses the Teamup API to make REST requests using the provided
        calendar ID, API Key, and optional Password.

        Provides access to a calendar's events, access keys, and some aspects of individual subcalendars.

        Parameters
        ----------
        cal_id - REQUIRED - string;
        api_key - REQUIRED - string;
        password - Optional - string;
        """
        self.__calendar_id = cal_id
        self.__api_key = api_key
        self.__cal_base = f'/{cal_id}'
        self.__token_str = f'?_teamup_token={self.api_key}'
        self.__headers = {'Content-type': 'application/json', 'Teamup-Token': self.__api_key}
        if password:
            self.__headers['Teamup-Password'] = password
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
    def headers(self):
        """read-only view of the headers used in API requests"""
        return self.__headers

    @property
    def api_key(self):
        """read-only view of the API key used in API requests"""
        return self.__api_key

    @property
    def calendar_id(self):
        """read-only view of the calendar key (id) used in API requests"""
        return self.__calendar_id

    @property
    def valid_api(self):
        """
        Helper property that returns True if the access check request returns 200

        Makes a request to the calendar to see if the api is valid. If error, writes the log message as ERROR

        Returns
        -------

        """
        if not self.__valid_api:
            try:
                make_request('get', self._check_access_url, headers=self.__headers)
                self.__valid_api = True
            except (TeamUpError, HTTPError) as e:
                logger.exception(e)
                self.__valid_api = False
        return self.__valid_api

    @property
    def keys(self):
        """Property that returns the current full key collection for a calendar. """
        self.__keys = self.get_key_collection()
        return self.__keys

    @property
    def configuration(self):
        if self.__configuration is None:
            print('Fetching configuration')
            url = self._base_url + CONFIGURATION_BASE
            req = make_request('get', url, self.__headers)
            self.__configuration = json.loads(req.text)['configuration']
        return self.__configuration

    @property
    def subcalendars(self):
        if not self.__subcalendars:
            print('Fetching Subcalendars')
            req = make_request('get', self._subcalendars_url, self.__headers)
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
        :param subcal_id: optional str or list-like if a different parent should be queried
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
        req = make_request('get', url, self.__headers)
        self.events_json = json.loads(req.text)['events']

        if returnas == 'events':
            return [Event(self, **event_dict) for event_dict in self.events_json]
        elif returnas == 'dataframe' and 'pandas' in sys.modules:
            return pd.DataFrame.from_records(self.events_json)
        else:
            return self.events_json

    def _create_event_from_json(self, payload):
        """ DEPRECATED
        Lazy Creation of Event by passing a json encoded string payload"""
        warn('Calendar._create_event_from_json is deprecated, use Calendar.new_event to construct a new event.',
             DeprecationWarning)
        return make_request('post', self._event_collection_url, self.__headers, payload)

    def get_event(self, event_id, returnas='event'):
        """
        Primary access method to fetch a single event. Event can be returned as Event Object, Python Dictionary, or
        Pandas Series
        Parameters
        ----------
        event_id - integer; ID of a valid event contained within a calendar.
        returnas - string; one of: 'event' | 'dict' | 'series'

        Returns
        -------
        object containing event data in format requested, default `Event` object
        """
        if returnas not in ('event', 'series', 'dict'):
            raise ValueError('Returnas not recognized. Recognized values: event, series, dict')

        url = self._base_url + EVENTS_BASE + f'/{event_id}'
        resp = make_request('get', url, self.__headers)

        event_dict = resp.json()['event']
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
        Method for accessing the API endpoint provided here: https://apidocs.teamup.com/?shell#get-events-changed

        Get changed events since given unix time, returns a tuple containing the iterable of events in the format
        specified in `returnas` AND the timestamp interpreted by the TeamUp server

        event_id - integer; ID of a valid event contained within a calendar.
        returnas - string; one of: 'event' | 'dict' | 'dataframe'

        Returns
        -------
        tuple containing
        collection of object containing event data in format requested, default a list of `Event` objects.
        """
        if returnas not in ('event', 'df', 'dict'):
            raise ValueError('Returnas not recognized. Recognized values: event, series, dict')
        url = self._base_url + EVENTS_BASE + '&modifiedSince=' + str(modified_since)
        resp = make_request('get', url, self.__headers)
        resp_json = resp.json()
        events_json = resp_json['events']
        timestamp = resp_json['timestamp']

        if returnas == 'event':
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

        Parameters
        ----------
        title - string (Required); Title of the event, must be
        start_dt - datetime (Required); Start Datetime of the event
        end_dt - datetime (Required); End Datetime
        subcalendar_ids: str, int, or list-like (Required); The ID of the subcalendar within the parent the event should be created in.
        all_day: bool; Event is all day or not
        notes - string; HTML or Markdown formatted string detailing the Description
        location - string; Location of the event
        who - string;
        remote_id - string; Remote ID of the event, used to link the TeamUp event record to its source information
        returnas - string; One of: 'event' | 'dict' | 'series' DEFAULT: 'event'

        Returns
        -------
        object containing created event data returned by the server in the format specified in `returnas` argument
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

        resp = make_request('post', self._event_collection_url, self.__headers, json.dumps(dict))
        resp_dict = resp.json()
        event_dict = resp_dict['event']
        undo_id = resp_dict['undo_id']

        if returnas == 'event':
            return Event(self, undo_id = undo_id, **event_dict)
        elif returnas == 'series' and 'pandas' in sys.modules:
            return pd.Series(event_dict)
        else:
            return event_dict

    def get_key_collection(self, returnas='key'):
        """
        Get the current key collection available to the calendar.
        Parameters
        ----------
        returnas - string; DEFAULT: 'key'; one of: 'key' | 'dict'

        Returns
        -------
        a tuple of returned keys in the format specified in `returnas` argument
        """
        if returnas not in ('key', 'dict'):
            raise ValueError('Return as must be one of: "key", "dict" ')
        resp = make_request('get', self._accesskey_url, headers=self.__headers)
        keys = resp.json()['keys']
        if returnas == 'key':
            return (Key(parent=self, **key) for key in keys)
        return tuple(keys)

    def get_key(self, key_id, returnas='key'):
        """
        Get the current key collection available to the calendar.
        Parameters
        ----------
        key_id - string (Required); the id of the key requested contained within the Calendar.
        returnas - string; DEFAULT: 'key'; one of: 'key' | 'dict'

        Returns
        -------
        a the data of the returned key in the format specified in `returnas` argument
        """
        if returnas not in ('key', 'dict'):
            raise ValueError('Return as must be one of: key, dict')

        url = self._accesskey_url + f'/{key_id}'
        resp = make_request('get', url, headers=self.__headers)
        keys_json = resp.json()
        if returnas == 'key':
            return Key(parent=self, **keys_json['key'])
        return keys_json['key']

    def create_key(self, key_name, key_share_type, key_perms, key_active=True, key_admin=False, key_require_pass=False,
                   key_pass="", key_all_other=None):
        """
        Method for creating keys for individual sub-calendars.

        Credit to Frederick Schaller IV (@LogicallyUnfit on Github) for main contribution.

        Parameters
        ----------
        key_name - string; name to give key
        key_share_type - string; the share type value, one of: all_subcalendars, selected_subcalendars
        key_perms - string OR dictionary; if key_share_type is all_subcalendars then pass string, if key_share_type is
                    selected_subcalendars then pass a dictionary with the subcalendar ID as the key, and the string
                    permission value (from Key.PERMISSIONS)
        key_active - Boolean
        key_admin - Boolean
        key_require_pass - Boolean
        key_pass - String; only provide if key_require_pass==True
        key_all_other - String; only pas if key_share_type=="selected_subcalendars", any subcalendars omitted from the
                        key_perms dict will be assigned this permission value. Recommended to set to 'no_access'

        Returns
        -------
        `Key` object containing newly created Key

        """
        if not isinstance(key_name, str):
            raise TypeError('Key name must be a string')
        if not isinstance(key_require_pass, bool):
            raise TypeError('Key require_pass must be a boolean')
        if key_share_type not in Key.SHARE_TYPES:
            raise ValueError(f'Invalid share type: {key_share_type}')

        payload = {
            "name": key_name,
            "active": key_active,
            "admin": key_admin,
        }

        if key_require_pass:
            # user wants to add a password
            payload['require_password'] = key_require_pass
            if not isinstance(key_pass, str):
                raise TypeError('Key pass must be a string')
            if key_pass == "":
                raise ValueError('Key password cannot be empty')
            payload['password'] = key_pass
        else:
            # user does not want to add a password
            payload['require_password'] = key_require_pass
            payload['password'] = ""

        if key_share_type == 'all_subcalendars':
            if key_perms not in Key.PERMISSIONS:
                raise ValueError(f'Invalid permission: {key_perms}')
            # All subcalendars have the same permissions
            payload['share_type'] = key_share_type
            payload['role'] = key_perms

        elif key_share_type == 'selected_subcalendars':
            if not isinstance(key_perms, dict):
                raise TypeError(f'Invalid key_perms: {key_perms}')
            payload['share_type'] = key_share_type
            payload['subcalendar_permissions'] = {}
            if key_all_other is not None:
                # Set all other subcalendars to specified permission
                if key_all_other not in Key.PERMISSIONS:
                    raise Exception(f'Invalid key_all_other value: {key_all_other}')
                subcalendars = Calendar(self.__calendar_id, self.__api_key).subcalendars
                for subcal in subcalendars:
                    payload['subcalendar_permissions'][str(subcal['id'])] = key_all_other
                payload['role'] = key_all_other
            for perm in key_perms:
                # Overwrite all other perm with specified perm
                if key_perms[perm] not in Key.PERMISSIONS:
                    raise Exception(f'Invalid key_perms: {key_perms}')
                payload['subcalendar_permissions'][perm] = key_perms[perm]

        payloadjson = json.dumps(payload)
        resp = make_request('post', self._accesskey_url, headers=self.__headers, payload=payloadjson)
        key_data = resp.json()['key']
        return Key(parent=self, **key_data)

    def find_key_by_name(self, key_name, case_sensitive=False, exact_match=False):
        # Finds a key by name, returns a tuple of keys that match the given criteria
        # GET /{calendarKey}/keys
        find = []
        for key in self.keys:
            if case_sensitive:
                if exact_match:
                    # Ex=T & Cs=T
                    if key_name == key.name:
                        find.append(key)
                else:
                    # Ex=F & Cs=T
                    if key_name in key.name:
                        find.append(key)
            else:
                if exact_match:
                    # Ex=T & Cs=F
                    if key_name.lower() == key.name.lower():
                        find.append(key)
                else:
                    # Ex=T & Cs=F
                    if key_name.lower() in key.name.lower():
                        find.append(key)

        if len(find) == 0:
            return ()
        return tuple(find)

    def find_key_by_perm(self):
        # Find keys with specific permissions
        # GET /{calendarKey}/keys
        raise NotImplementedError

    def find_key_by_date(self):
        # Find keys created in time frame.
        # GET /{calendarKey}/keys
        raise NotImplementedError

    def delete_key(self, key):
        # Deletes a key for the parent
        # DELETE /{calendarKey}/keys/{keyId}
        if isinstance(key, Key):
            key_id = key.id
        elif isinstance(key, int):
            key_id = key
        else:
            raise TypeError('Key id must be an integer or Key object')

        url = self._accesskey_url + f'/{str(key_id)}'
        make_request('delete', url, headers=self.__headers)
        return True
