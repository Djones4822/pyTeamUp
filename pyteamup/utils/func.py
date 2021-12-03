"""
functions for pyteamup
"""
import datetime
from pyteamup.utils.const import RESPONSES
from pyteamup.utils.error import TeamUpError
from urllib.error import HTTPError
import json
from json.decoder import JSONDecodeError
import logging
import requests

logger = logging.getLogger(__name__)


def check_status_code(status_code, response=None, url=None, headers=None, fp=None):
    """
    Utility function for checking the result of a response. requires status code, pass the response to get
    the server message as a TeamUpError rather than HTTPError. Otherwise returns the message.
    """
    if status_code >= 400:
        if not isinstance(response, dict):
            try:
                response = json.loads(response)
            except JSONDecodeError as e:
                logger.error('Cannot decode response')
                logger.exception(e)
                response = None
        if response:
            error_msg = response['error']['message']
            error_title = response['error']['title']
            raise TeamUpError(f'Response {status_code} - {error_title}: {error_msg}')
        raise HTTPError(url, status_code, RESPONSES.get(status_code, 'Unknown Error'), hdrs=headers, fp=fp)
    return RESPONSES.get(status_code, f'Unknown but Ok: {status_code}')


def format_date(date):
    if not isinstance(date, datetime.datetime):
        raise TypeError
    if date.tzinfo is None:
        return date.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        return date.strftime('%Y-%m-%dT%H:%M:%S%z')

def make_request(method, url, headers, payload=None):
    if method.lower() == 'get':
        req = requests.get(url, headers=headers)
    if method.lower() == 'post':
        req = requests.post(url, headers=headers, data=payload)
    if method.lower() == 'put':
        req = requests.put(url, headers=headers, data=payload)
    if method.lower() == 'delete':
        req = requests.put(url, headers=headers, data=payload)
    check_status_code(req)
    return req