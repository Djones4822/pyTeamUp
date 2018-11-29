import requests
import json
import datetime
from warnings import warn

from pyteamup.utils import *

class Calendar:
    BASE_URL = f'https://api.teamup.com'
    CHECK_ACCESS_BASE = '/check-access'
    EVENTS_BASE = '/events'
    SUBCALENDARS_BASE = '/subcalendars'
    CONFIGURATION_BASE = '/configuration'
    POST_HEADERS = {'Content-type':'application/json'}

    def __init__(self, cal_id, api_key):
        self.__calendar_id = cal_id
        self.__api_key = api_key
        self.__valid_api = None
        self.__cal_base = f'/{cal_id}'
        self.__configuration = None
        self.__token_str = f'?_teamup_token={self.api_key}'

        self._base_url = Calendar.BASE_URL + self.__cal_base
        self._events_url = self._base_url + Calendar.EVENTS_BASE + self.__token_str
        self._subcalendars_url = self._base_url + Calendar.SUBCALENDARS_BASE + self.__token_str
        self._check_access_url = Calendar.BASE_URL + Calendar.CHECK_ACCESS_BASE + self.__token_str
        self._session_request_counter = 0

        if not self.valid_api:
            raise Exception(f'Invalid Api Key: {self.api_key}')

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
                self._session_request_counter += 1
                self.__valid_api = True
            except:
                self.__valid_api = False
            return self.__valid_api

        else:
            return

    @property
    def configuration(self):
        """"""
        if self.__configuration is None:
            req = requests.get(self._base_url + Calendar.CONFIGURATION_BASE + self.__token_str)
            check_status_code(req.status_code)
            self.__configuration = json.loads(req.text)['configuration']
        return self.__configuration

    def get_events(self, start_date=None, end_date=None, subcal_id=None):
        """
        Method allows bulk fetching of events that fall between the provided time frame. If None is provided then
        the current date -30 and +180 days is used.

        :param start_date: if set as None then set as today minus 30 days
        :param end_date:  if left as None then set as today plus 180 days
        :param subcal_id: optional str or list-like if a different calendar should be queried
        :return: json of events
        """
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
        req = requests.get(self._events_url + parameters)
        check_status_code(req.status_code)
        self.events_json = json.loads(req.text)
        return self.events_json

    def create_event(self, payload):
        """ Lazy Creation of Event by passing a formatted payload"""
        resp = requests.post(self._events_url, data=payload, headers=Calendar.POST_HEADERS)
        check_status_code(resp.status_code)
        #raise NotImplementedError

    def update_event(self, event_id, payload):
        """ Lazy Update of Event by passing an event ID and a formatted payload"""
        raise NotImplementedError

    def delete_event(self, event_id):
        """ Lazy Delete of an event by passing the event id"""
        raise NotImplementedError


if __name__ == '__main__':
    pass