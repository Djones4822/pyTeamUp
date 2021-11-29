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