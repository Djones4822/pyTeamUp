"""
Constants for PyTeamUp package

Author: David Jones
Creation Date: 11/27/2017
Last Updated 12/3/2021
"""
BASE_URL = f'https://api.teamup.com'
CHECK_ACCESS_BASE = '/check-access'
EVENTS_BASE = '/events'
KEYS_BASE = '/keys'
SUBCALENDARS_BASE = '/subcalendars'
CONFIGURATION_BASE = '/configuration'
POST_HEADERS = {'Content-type': 'application/json'}

KEY_PERMISSIONS = (
    "admin",
    "modify",
    "modify_from_same_link",
    "add_only",
    "read_only",
    "modify_from_same_link_without_details",
    "add_only_without_details",
    "read_only_without_details",
    "no_access"
)

KEY_ROLES = ('mixed', *KEY_PERMISSIONS)

KEY_SHARE_TYPES = (
    "all_subcalendars",
    "selected_subcalendars"
)

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

# colors as of 12/3/2021 - https://apidocs.teamup.com/?shell#colors
COLORS = {
    1: ' #f2665b',
    2: ' #cf2424',
    3: ' #a01a1a',
    4: ' #7e3838',
    5: ' #ca7609',
    6: ' #f16c20',
    7: ' #f58a4b',
    8: ' #d2b53b',
    9: ' #d96fbf',
    10: ' #b84e9d',
    11: ' #9d3283',
    12: ' #7a0f60',
    13: ' #542382',
    14: ' #7742a9',
    15: ' #8763ca',
    16: ' #b586e2',
    17: ' #668CB3',
    18: ' #4770d8',
    19: ' #2951b9',
    20: ' #133897',
    21: ' #1a5173',
    22: ' #1a699c',
    23: ' #0080a6',
    24: ' #4aaace',
    25: ' #88b347',
    26: ' #5a8121',
    27: ' #2d850e',
    28: ' #176413',
    29: ' #0f4c30',
    30: ' #386651',
    31: ' #00855b',
    32: ' #4fb5a1',
    33: ' #553711',
    34: ' #724f22',
    35: ' #9c6013',
    36: ' #f6c811',
    37: ' #ce1212',
    38: ' #b20d47',
    39: ' #d8135a',
    40: ' #e81f78',
    41: ' #f5699a',
    42: ' #5c1c1c',
    43: ' #a55757',
    44: ' #c37070',
    45: ' #000000',
    46: ' #383838',
    47: ' #757575',
    48: ' #a3a3a3',
}

# error messages as of 12/3/2021 - https://apidocs.teamup.com/?shell#error-ids
ERROR_MESSAGES = {
    'maintenance_active': 'The application is in maintenance mode.',
    'unexpected_error': 'The application experienced an unexpected error.',
    'auth_required': 'Authentication is required to access this calendar key, you must provide a Teamup-Password header.',
    'no_permission': 'You do not have the permissions to do this, you may be using a readonly calendar key for example.',
    'event_add_only_permission_expired': 'If you use an add-only calendar key, events created can not be updated via the API.',
    'calendar_not_found': 'You use an invalid calendar key.',
    'event_not_found': 'The event id was not found.',
    'field_definition_not_found': 'The field id was not found.',
    'validation_error': 'The provided data did not validate.',
    'event_overlapping': 'You tried to create an event conflicting with an existing event on a sub-calendar that does not allow overlap.',
    'event_validation': 'You provided invalid event data when updating or creating an event. See the message key for details.',
    'event_validation_conflict': 'You tried to update or delete an event using an outdated version property because someone else modified it since you last read the event.',
    'invalid_timezone_identifier': 'Invalid timezone identifier provided.',
    'invalid_api_key': 'Invalid API Key provided.',
    'field_id_reserved': 'This is a built-in or reserved field ID, so a field with that ID cannot be directly created or deleted.',
    'field_id_not_unique': 'There is already a field with that ID.',
    'field_type_reserved': 'This is a built-in field type, so a field with that type cannot be directly created.',
    'field_limit_exceeded': 'Creating or enabling this field would make the calendar exceed its subscription plan\'s limit on the number of custom fields.',
    'field_choice_limit_exceeded': 'Creating or enabling this field would make it exceed its calendar\'s subscription plan\'s limit on the number of custom field choices.',
    'field_choice_removed': 'You attempted to update a field definition and omitted a choice definition that was previously present.',
}