import requests
import json
import datetime

class Calendar:
    BASE_URL = f'https://api.teamup.com'
    CHECK_ACCESS_BASE = '/check-access'
    EVENTS_BASE = '/events'
    SUBCALENDARS_BASE = '/subcalendars'

    def __init__(self, cal_id, api_key=None):
        self.calendar_id = cal_id
        self.api_key = api_key
        self._cal_base = f'/{cal_id}'

    @staticmethod
    def check_status_code(status_code):
        if status_code == 400:
            raise Exception('400: Bad Request -- Invalid Request')
        elif status_code == 401:
            raise Exception('401: Unauthorized -- Accessing a password-protected resource without providing authentication')
        elif status_code == 403:
            raise Exception('403: Forbidden -- Invalid credentials to access the given resource')
        elif status_code == 404:
            raise Exception('404: Not Found -- Resource missing, not found or not visible by your request')
        elif status_code == 405:
            raise Exception('405: Method Not Allowed -- You tried to access a resource with an invalid method (i.e. GET instead of POST)')
        elif status_code == 406:
            raise Exception('406: Not Acceptable -- You requested a format that is not json')
        elif status_code == 415:
            raise Exception('415: Unsupported Media Type -- The server is refusing to service the request because the payload is in a format not supported. Make sure you have the headers Content-Type: application/json and Content-Encoding properly set.')
        elif status_code == 500:
            raise Exception('500: Internal Server Error -- Application error on TeamUp side, TeamUp will look into it but feel free to reach out with details.')
        elif status_code == 503:
            raise Exception('503: Service Unavailable -- We are temporarially offline for maintanance. Please try again later.')
        elif status_code == 200:
            return 'Ok'
        elif status_code == 201:
            return 'Created'
        elif status_code == 204:
            return 'No content'
        else:
            return f'Unknown but Ok: {status_code}'

    @property
    def _token_str(self):
        if not self.api_key:
            raise Exception('No API Key Set')
        return f'?_teamup_token={self.api_key}'

    @property
    def _base_url(self):
        return Calendar.BASE_URL + self._cal_base

    @property
    def _events_url(self):
        return self._base_url + Calendar.EVENTS_BASE + self._token_str

    @property
    def _subcalendars_url(self):
        return self._base_url + Calendar.SUBCALENDARS_BASE + self._token_str

    @property
    def _check_access_url(self):
        return Calendar.BASE_URL + Calendar.CHECK_ACCESS_BASE + self._token_str

    def check_access(self):
        req = requests.get(self._check_access_url)
        self.check_status_code(req.status_code)
        resp = json.loads(req.text)
        access = resp['access']

        if access.lower() != 'ok':
            raise Exception(f'Invalid response text: {access}')
        else:
            return True
            #return check_access_url, req

    def get_events(self, start_date=None, end_date=None, subcal_id=None):
        """
        Method allows bulk fetching of events that fall between the provided time frame. If None is provided then
        the current date -30 and +180 days is used.

        :param start_date: if set as None then set as today minus 30 days
        :param end_date:  if left as None then set as today plus 180 days
        :param cal_id: optional str or list-like if a different calendar should be queried
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
        self.check_status_code(req.status_code)
        self.events_json = json.loads(req.text)
        return self.events_json

    def create_event(self, payload):
        """ Lazy Creation of Event by passing a formatted payload"""
        resp = requests.post(self._events_url, data=payload)
        self.check_status_code(resp.status_code)
        #raise NotImplementedError

    def update_event(self, event_id, payload):
        """ Lazy Update of Event by passing an event ID and a formatted payload"""
        raise NotImplementedError

    def delete_event(self, event_id):
        """ Lazy Delete of an event by passing the event id"""
        raise NotImplementedError


