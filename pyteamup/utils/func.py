"""
Utility Functions for PyTeamUp

Author: David Jones
Creation Date: 11/27/2017
Last Updated 12/3/2021
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
    Utility function for checking the result of a Teamup API response. requires status code, pass the response to get
    the server message as a TeamUpError rather than HTTPError. Otherwise returns the message.

    Not intended for any other use than the TeamUp API

    Parameters
    ----------
    status_code - required, should be from response.status_code
    response - requests.response object OR python dictionary of decoded response JSON
    url - optional, for HTTPError which is raised if the response is malformed or not from Teamup
    headers - optional, for HTTPError which is raised if the response is malformed or not from Teamup
    fp - optional, for HTTPError which is raised if the response is malformed or not from Teamup

    Returns
    -------

    """
    if status_code >= 400:
        if isinstance(response, requests.Response):
            try:
                response = json.loads(response.text)
            except JSONDecodeError as e:
                logger.error('Cannot decode response')
                logger.exception(e)
                response = None
        if response and 'error' in response.keys():
            error_msg = response['error']['message']
            error_title = response['error']['title']
            raise TeamUpError(f'Response {status_code} - {error_title}: {error_msg}')
        raise HTTPError(url, status_code, RESPONSES.get(status_code, 'Unknown Error'), hdrs=headers, fp=fp)
    return RESPONSES.get(status_code, f'Unknown but Ok: {status_code}')


def format_date(date):
    """
    Helper to easily format dates with or without timezones.
    Parameters
    ----------
    date - datetime object

    Returns
    -------
    string containing formatted text, uses mask: %Y-%m-%dT%H:%M:%S%z
    """
    if not isinstance(date, datetime.datetime):
        raise TypeError
    if date.tzinfo is None:
        return date.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        return date.strftime('%Y-%m-%dT%H:%M:%S%z')


def make_request(method, url, headers=None, payload=None):
    """
    Function to make requests - intended for teamup only, checks the response using `check_status_code()`.

    Added to reduce code duplication.

    Parameters
    ----------
    method
    url
    headers - python dictionary of header options
    payload - json string, do not pass a python dictionary

    Returns
    -------
    requests.Response object
    """
    m = method.lower()
    if m == 'get':
        resp = requests.get(url, headers=headers)
    elif m == 'post':
        resp = requests.post(url, headers=headers, data=payload)
    elif m == 'put':
        resp = requests.put(url, headers=headers, data=payload)
    elif m == 'delete':
        resp = requests.delete(url, headers=headers)
    else:
        raise ValueError(f'Unknown Method type {method}')

    try:
        check_status_code(resp.status_code, resp)
    except TeamUpError as e:
        if payload:
            logger.error(f'Payload sent with request:\n{payload}')
        raise e

    return resp