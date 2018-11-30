import datetime
from time import gmtime, strftime

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
        raise Exception(
            '405: Method Not Allowed -- You tried to access a resource with an invalid method (i.e. GET instead of POST)')
    elif status_code == 406:
        raise Exception('406: Not Acceptable -- You requested a format that is not json')
    elif status_code == 415:
        raise Exception(
            '415: Unsupported Media Type -- The server is refusing to service the request because the payload is in a format not supported. Make sure you have the headers Content-Type: application/json and Content-Encoding properly set.')
    elif status_code == 500:
        raise Exception(
            '500: Internal Server Error -- Application error on TeamUp side, TeamUp will look into it but feel free to reach out with details.')
    elif status_code == 503:
        raise Exception(
            '503: Service Unavailable -- We are temporarially offline for maintanance. Please try again later.')
    elif status_code == 200:
        return 'Ok'
    elif status_code == 201:
        return 'Created'
    elif status_code == 204:
        return 'No content'
    else:
        return f'Unknown but Ok: {status_code}'


def get_sys_utc_offset_str():
    return (strftime("%z", gmtime()))

def format_date(date):
    if not isinstance(date, datetime.datetime):
        raise TypeError
    tz_offset = get_sys_utc_offset_str()
    return date.strftime('%Y-%m-%dT%H:%M:%S') + tz_offset

