import requests
import json
from warnings import warn

from pyteamup.utils.utilities import *
from pyteamup.utils.constants import *
#from pyteamup.Calendar import Calendar

class Key:
    PERMISSIONS = KEY_PERMISSIONS
    SHARE_TYPES = KEY_SHARE_TYPES
    ROLES = KEY_ROLES

    def __init__(self, calendar, id=None, name=None, key=None, active=None, admin=None, share_type=None, role=None, subcalendar_permissions=None,
                 require_password=None, has_password=None, email=None, user_id=None, creation_dt=None, update_dt=None, **kwargs):

        #if not isinstance(calendar, Calendar):
        #    raise TypeError('Must pass a valid Calendar object for Key')

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
        self.__email = email  # always null? No interface specified in API Documentation as of 11/29/2021
        self.__user_id = user_id  # always null? No interface specified in API Documentation as of 11/29/2021
        self.__creation_dt = creation_dt
        self.__update_dt = update_dt

        for k in kwargs:
            warn(f'Unknown keyword {k}')

        self.__url = self.__calendar._accesskey_url + f'/{self.__id}'

    def __str__(self):
        return f'{str(self.__id)}'

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name):
        if not isinstance(new_name, str):
            raise TypeError(f'Key Names must be string type, not {type(new_name)}')
        self.update(name=new_name)

    @property
    def key(self):
        return self.__key

    @property
    def active(self):
        return self.__active

    @active.setter
    def active(self, new_active):
        if not isinstance(new_active, bool):
            raise TypeError(f'Key Names must be boolean type, not {type(new_active)}')
        self.update(active=new_active)

    @property
    def admin(self):
        return self.__admin

    @admin.setter
    def admin(self, new_admin):
        if not isinstance(new_admin, bool):
            raise TypeError(f'Key Names must be boolean type, not {type(new_admin)}')
        self.update(admin=new_admin)

    @property
    def share_type(self):
        return self.__share_type

    @share_type.setter
    def share_type(self, x):
        raise Exception('Cannot set via property setter, use Key.update() method to change share_type')

    @property
    def role(self):
        return self.__role

    @role.setter
    def role(self, x):
        raise Exception('Cannot set via property setter, use Key.update() method to change role')

    @property
    def subcalendar_permissions(self):
        return self.__subcalendar_permissions

    @subcalendar_permissions.setter
    def subcalendar_permissions(self, x):
        raise Exception('Cannot set via property setter, use Key.update() method to change subcalendar_permissions')

    @property
    def require_password(self):
        return self.__require_password

    @require_password.setter
    def require_password(self, x):
        raise Exception('Cannot set via property setter, use Key.update() method to change require_password')

    @property
    def has_password(self):
        return self.__has_password

    @property
    def creation_dt(self):
        return self.__creation_dt

    @property
    def update_dt(self):
        return self.__update_dt

    @property
    def as_dict(self):
        return {
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
        }

    def update(self, **kwargs):
        """
        Method for updating the attributes of a key. Makes minimal assumptions about the Key and permissions, relying
        on the Server to provide feedback.

        For example, if you set a permission for role, and also provide permissions for individual subcalendars,
        or some other mis-configuration, the method will pass the misconfiguration to the Server for evaluation and
        response.

        Can pass one value or many. No Batch mode.

        Will raise ValueError if an invalid key is provided in kwargs.

        Credit to Frederick Schaller IV (@LogicallyUnfit on Github) for initial contribution.

        Parameters
        ----------
        kwargs - can be any of the fields specified in the API documentation as writable. See documentation for
                 more information. Fields that can be updated are:
                    name - string;
                    key_share_type - string; will raise ValueError if invalid value provided
                    role - string; will raise ValueError if invalid value provided
                    active - boolean
                    admin - boolean
                    require_password - boolean
                    password - string, required if setting require_password=True
                    subcalendar_permissions - empty list or dictionary of subcalendar ID's and the new permission

        Returns
        -------
        None, will update the values of the Key Object in place.

        """
        if not kwargs:
            raise ValueError('Must pass property to update')

        # Load existing key data
        payload = self.as_dict

        for key, value in kwargs.items():
            if key not in payload.keys():
                raise ValueError(f'Unknown property {key}')

            if key in ('id', 'key', 'creation_dt', 'update_dt'):
                raise ValueError(f'Cannot update {key}')

            if key == 'name':
                if not isinstance(value, str):
                    raise TypeError(f'Key name must be a string not {type(value)}')
            elif key == 'key_share_type':
                if value not in Key.SHARE_TYPES:
                    raise ValueError(f'Invalid share type: {value}')
            elif key == 'role':
                if value not in Key.ROLES:
                    raise ValueError(f'Invalid role value: {value}')
            elif key == 'active':
                if not isinstance(value, bool):
                    raise TypeError('active parameter must be a boolean')
            elif key == 'admin':
                if not isinstance(value, bool) :
                    raise Exception('admin parameter must be a boolean')
            elif key == 'require_password':
                if not isinstance(value, bool):
                    raise Exception('require_pass parameter must be a boolean')
                if value:
                    if 'password' not in kwargs:
                        raise KeyError('password parameter must be present if adding password requirement')
                else:
                    payload['password'] = ""
            elif key == 'password':
                if not isinstance(value, str):
                    raise Exception(f'Key pass must be a string not {type(value)}')

            elif key == 'subcalendar_permissions':
                if value != [] and not isinstance(value, dict):
                    raise TypeError('subcalendar_permissions must be one of: empty list or dictionary')
                if isinstance(value, dict):
                    if not payload['subcalendar_permissions']:
                        payload['subcalendar_permissions'] = {}
                    for subcal_id, perm in value.items():
                        if perm not in Key.PERMISSIONS:
                            raise ValueError(f'Invalid permission: {perm}')
                        payload['subcalendar_permissions'][subcal_id] = perm
                    continue  # goto next key in kwargs
            payload[key] = value

        # Remove Read only bits that we can't modify
        payload.pop('update_dt', None)
        payload.pop('creation_dt', None)
        payload.pop('has_password', None)

        payloadjson = json.dumps(payload)

        req = requests.put(self.__url, headers=self.__calendar.headers, data=payloadjson)
        check_status_code(self.__url, req.status_code, self.__calendar.headers)
        return_data = json.loads(req.text)
        for k,v in return_data['key'].items():
            super(Key, self).__setattr__(f'_Key__{k}', v)
            #self.__setattr__(f'_Key__{k}', v)

    def get_key_events(self):
        # Returns events for a key
        # GET /{calendarKey}/keys
        raise NotImplementedError