import datetime
from urllib.error import HTTPError

RESPONSES = {
    400: '400: Bad Request -- Invalid Request',
    401: '401: Unauthorized -- Accessing a password-protected resource without providing authentication',
    403: '403: Forbidden -- Invalid credentials to access the given resource',
    404: '404: Not Found -- Resource missing, not found or not visible by your request',
    405: '405: Method Not Allowed -- You tried to access a resource with an invalid method (i.e. GET instead of POST)',
    406: '406: Not Acceptable -- You requested a format that is not json',
    415: '415: Unsupported Media Type -- The server is refusing to service the request because the payload is in a format not supported. Make sure you have the headers Content-Type: application/json and Content-Encoding properly set.',
    500: '500: Internal Server Error -- Application error on TeamUp side, TeamUp will look into it but feel free to reach out with details.',
    503: '503: Service Unavailable -- We are temporarially offline for maintanance. Please try again later.',
    200: 'Ok',
    201: 'Created',
    204: 'No content'
}


def check_status_code(url, status_code, headers=None, fp=None):
    if status_code >= 400:
        raise HTTPError(url, status_code, RESPONSES.get(status_code), hdrs=headers, fp=fp)
    return RESPONSES.get(status_code, f'Unknown but Ok: {status_code}')


def format_date(date):
    if not isinstance(date, datetime.datetime):
        raise TypeError

    if date.tzinfo is None:
        return date.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        return date.strftime('%Y-%m-%dT%H:%M:%S%z')

