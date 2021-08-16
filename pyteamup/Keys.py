from warnings import warn
import requests
import json
from datetime import datetime
from collections import OrderedDict
from dateutil.parser import parse as to_datetime

from pyteamup.utils.utilities import *
from pyteamup.utils.constants import *
from pyteamup.Calendar import Calendar

class Keys:
    def __init__(self, cal_id, api_key):
        self.__calendar_id = cal_id
        self.__api_key = api_key
        self.__valid_api = None
        self.__url = BASE_URL

        self._headers = {'Teamup-Token': self.__api_key}
        self._json_headers = {'Content-type': 'application/json', 'Teamup-Token': self.__api_key}
        self._base_url = BASE_URL + '/' + cal_id
        self._keys_url = self._base_url + KEYS_BASE
        self._check_access_url = BASE_URL + CHECK_ACCESS_BASE

        self.keys_json = None

        if not self.valid_api:
            raise Exception(f'Invalid Api Key: {self.__api_key}')
    
    def __str__(self):
        return str(self.get_keys())

    @property
    def valid_api(self):
        # Makes a request to the calendar to see if the api is valid
        if not self.__valid_api:
            req = requests.get(self._check_access_url, headers=self._headers)
            try:
                check_status_code(req.status_code)
                self.__valid_api = True
            except:
                self.__valid_api = False
            return self.__valid_api

        else:
            return None
    
    @property
    def url(self):
        return self._keys_url
    
    @property
    def share_types(self):
        # Share type options:
        share_types = {
            "all_subcalendars",
            "selected_subcalendars"
        }
        return share_types
    
    @property
    def permissions(self):
        # Permission options:
        permissions = {
            "admin",
            "modify",
            "modify_from_same_link",
            "add_only",
            "read_only",
            "modify_from_same_link_without_details",
            "add_only_without_details",
            "read_only_without_details",
            "no_access"
        }
        return permissions

    def get_keys(self):
        # Returns all keys for the calendar
        # GET /{calendarKey}/keys
        req = requests.get(self.url, headers=self._headers)
        check_status_code(req.status_code)
        self.keys_json = json.loads(req.text)
        return self.keys_json['keys']
    
    def get_key(self, key_id):
        # Returns a key for the calendar
        # GET /{calendarKey}/keys/{keyId}
        req = requests.get(self.url + f'/{key_id}', headers=self._headers)
        check_status_code(req.status_code)
        self.keys_json = json.loads(req.text)
        return self.keys_json['key']
        
    def create_key(self, key_name, key_share_type, key_perms, key_active=True, key_admin=False, key_require_pass=False, key_pass="", key_all_other=None):
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
        keys = self.get_keys()
        find = []
        for key in keys:
            if case_sensitive == True:
                if exact_match == True:
                    # Ex=T | Cs=T
                    if key_name == key['name']:
                        find.append(key)
                else:
                    # Ex=F | Cs=T
                    if key_name in key['name']:
                        find.append(key)
            else:
                if exact_match == True:
                    # Ex=T | Cs=F
                    if key_name.lower() == key['name'].lower():
                        find.append(key)
                else:
                    # Ex=T | Cs=F
                    if key_name.lower() in key['name'].lower():
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
    
    def delete_key(self, key_id):
        # Deletes a key for the calendar
        # DELETE /{calendarKey}/keys/{keyId}
        if isinstance(key_id, int) == False:
            raise Exception('Key id must be an integer')

        req = requests.delete(self.url + '/' + str(key_id), headers=self._headers)
        if req.status_code == 204:
            return True
        else:
            check_status_code(req.status_code)
            return False
    
    def get_key_events(self):
        # Returns events for a key
        # GET /{calendarKey}/keys
        raise NotImplementedError