from warnings import warn
import requests
import json
from datetime import datetime
from collections import OrderedDict
from dateutil.parser import parse as to_datetime

from pyteamup.utils.utilities import *
from pyteamup.utils.constants import *
from pyteamup.Calendar import Calendar

class Key:
    permissions = KEY_PERMISSIONS
    share_types = KEY_SHARE_TYPES

    def __init__(self, calendar, id=None, name=None, key=None, active=None, admin=None, share_type=None, role=None, subcalendar_permissions=None,
                 require_password=None, has_password=None, email=None, user_id=None, creation_dt=None, update_dt=None):

        if not isinstance(calendar, Calendar):
            raise TypeError('Must pass a Calendar object to construct a Key')

        if not calendar.valid_api:
            raise ValueError('Calendar object does not have a valid API key')

        self.__calendar = calendar
        self.__id = id
        self.__name = name
        self.__key = key
        self.__active = active
        self.__admin = admin
        self.__share_type = share_type
        self.__role = role
        self.__subcalendar_permissions = subcalendar_permissions
        self.__require_password = require_password
        self.__has_password = has_password
        self.__email = email
        self.__user_id = user_id
        self.__creation_dt = creation_dt
        self.__update_dt = update_dt

    def __str__(self):
        return f'Calendar Key {self.__id}'

    @property
    def as_json(self):
        return json.dumps({
            'id': self.__id,
            'name': self.__name,
            'key': self.__key,
            'active': self.__active,
            'admin': self.__admin,
            'share_type': self.__share_type,
            'role': self.__role,
            'subcalendar_permissions': self.__subcalendar_permissions,
            'require_password': self.__require_password,
            'has_password': self.__has_password,
            'creation_dt': self.__creation_dt,
            'update_dt': self.__update_dt
        })

    def update_key(self, key_id, key_name=None, key_share_type=None, key_perms=None, key_active=None, key_admin=None, key_require_pass=None, key_pass=None, key_all_other=None):
        # Updates a key for the calendar
        # PUT /{calendarKey}/keys/{keyId}
        if key_name == None and key_share_type == None and key_perms == None and key_active == None and key_admin == None and key_require_pass == None and key_pass == None and key_all_other == None:
            raise Exception('No updates specified')
        if isinstance(key_id, int) == False:
            raise Exception('Key id must be an integer')

        # Load existing key        
        payload = self.get_key(key_id)
        
        # Update elements
        if key_name != None:
            if isinstance(key_name, str) == False:
                raise Exception('Key name must be a string')
            payload['name'] = key_name
        if key_share_type != None:
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
        if key_active != None:
            if isinstance(key_active, bool) == False:
                raise Exception('Key active must be a boolean')
            payload['active'] = key_active
        
        if key_admin != None:
            if isinstance(key_admin, bool) == False:
                raise Exception('Key admin must be a boolean')
            payload['admin'] = key_admin
        
        if key_require_pass != None:
            if key_pass == None:
                raise Exception('Key require_password requires a password')
            if isinstance(key_require_pass, bool) == False:
                raise Exception('Key require_pass must be a boolean')
            if key_require_pass == True:
                if isinstance(key_pass, str) == False:
                    raise Exception('Key pass must be a string')
                payload['require_password'] = key_require_pass
                payload['password'] = key_pass
            else:
                payload['require_password'] = key_require_pass
                payload['password'] = ""
        # Remove Read only bits that we can't modify
        payload.pop('update_dt', None)
        payload.pop('creation_dt', None)
        payload.pop('type', None)
        payload.pop('has_password', None)

        payloadjson = json.dumps(payload)

        req = requests.put(self.url + '/' + str(key_id), headers=self._json_headers, data=payloadjson)
        check_status_code(req.status_code)
        self.keys_json = json.loads(req.text)
        return self.keys_json['key']

    def get_key_events(self):
        # Returns events for a key
        # GET /{calendarKey}/keys
        raise NotImplementedError