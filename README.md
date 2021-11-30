# pyTeamUp
Python API wrapper for TeamUp API. 

**Latest Version**: 0.1.5a-ALPHA (available in `accesskeys` build)  
**Latest Stable Version**: 0.1.4a (available via pip)

**Note**: version 0.1.4a or higher is required for working with the TeamUp API as of 11/26/2021. This version adds basic support for `atttachment` event attribute, but  since it is undocumented in the official API there is no way to add or remove attachments. They can be viewed using `event.attachments` if set through the Web interface.

**Note2**: 0.1.5a-ALPHA includes experimental `Key` object, as well as certain changes that may break existing code. Specifically, all `Exception`s are now raised as more informative `TypeError` or `ValueError` or `HTTPError`. A mostly complete list of changes and additions is available in the version history below.

## Installation
python 3.6 or higher required. Use pip (Current Version: 0.1.4a):
```
python -m pip install pyTeamUp
```

## Features:
 * Pythonic access to TeamUp Calendars, Events, and Access Keys.
 * Methods for gathering subcalendars and event collections. 
 * Interface for getting, creating and deleting events within `Calendar` object
 * Interface for getting, creating and deleting keys using the `Calendar` object methods (currently untested)
 * `Event` Object features simple interface for updating event properties 
 * `Key` object allows update key properties using the `update()` method (currently untested)
 * Batch update events to reduce api calls when updating multiple event properties
 * If pandas is present, Calendar can return events as Series objects and event collections as DataFrame objects

## Example usage 
```python
from pyteamup import Calendar, Event, Key
from datetime import datetime

api_key = 'example api key'           # Get your own here: https://teamup.com/api-keys/request
calendar_id = 'example calendar id'   # goto www.teamup.com to sign up and get your own calendar

# Instantiate the calendar
calendar = Calendar(calendar_id, api_key)

# Get Subcalendars
subcalendars = calendar.subcalendars
subcal = subcalendars[0]

# Easily Create new events
new_event_dict = {'title': 'New Event Title',
                  'start_dt': datetime(2018,11,29, 14, 0, 0),
                  'end_dt': datetime(2018, 11, 29, 14, 0, 0),
                  'subcalendar_ids': subcal['id'],
                  'notes': 'This is the description!'}
new_event = calendar.new_event(**new_event_dict, returnas='event')
print(new_event.event_id)

# Gather Event Collections (returns a list)
event_list = calendar.get_event_collection()    # Note that the default start_dt and end_dt are -30 days and +180 days from today respectively
evnt = event_list.pop()

# Simple change of the title
print(evnt.title)
evnt.title = 'New Title'
print(evnt.title)

# Batch Mode Updates
evnt.enable_batch_update()
evnt.title = 'New Title 2'           # Will display a warning that no changes are made until batch_commit() is called
print(evnt.title)                    # Will still print the old title
print(evnt.notes)
evnt.notes = 'New Notes!'            # Will display a warning that no changes are made until batch_commit() is called

evnt.batch_commit()
print(evnt.title)
print(evnt.notes)

# Prevented from Editing Read-Only Attributes
evnt.event_id = 123                  # Will raise an error because attribute is read-only

# Easy Delete and confirm
evnt.delete()
print(evnt.is_deleted)               # Will return True

# Gather keys already created for a Calendar
keys = calendar.get_key_collection(returnas='key')
# or
keys = calendar.keys                 # easy property accessor, identical output to get_key_collection
# or
key = calendar.get_key(123456)       # access an individual key by passing it the ID here

# Inspect Key information
print(key.as_dict)                

# Delete keys
calendar.delete_key(key)            # can pass a Key object, or the integer ID representing a Key (not the `key` value itself)
print(calendar.keys)                # Will return the tuple of keys excluding what was just deleted

# Create new Access Key with singular role of "read_only" 
jt_key = calendar.create_key(key_name='Johnny Test', key_share_type='all_subcalendars', key_perms='read_only') 

# Construct your calendar permissions 
myperms = {                                             # Each permission applies to specified Subcalendar
    "000001": "modify",                                 # Allows Key to Read, Add and Modify all events for subcal 000001
    "000002": "modify_from_same_link",                  # Allows Key to Read, Add and Modify events made by this key to subcal 000002
    "000003": "add_only",                               # Allows Key to Read and Add events to subcal 000003
    "000004": "read_only",                              # Allows Key to Read events of subcal 000004
    "000005": "modify_from_same_link_without_details",  # Allows Key to Read, Add and Modify events of subcal 000005 that were created by this key, Titles Only
    "000006": "add_only_without_details",               # Allows Key to Read and Add events of subcal 000006, Titles Only
    "000007": "read_only_without_details",              # Allows Key to Read events of subcal 000007, Titles Only
    "000008": "no_access",                              # Key has no access to subcal 000008 
}

# Create a new Access Key with individual permissions per subcaledar
tt_key = calendar.create_key('Tommy Test', key_share_type='selected_subcalendars', key_perms=myperms, key_all_other='read_only') # key_all_other sets remaining calendars and default for new calendars. if omitted, default is no_access

# Update Tommy's key name using property setter.
tt_key.name = 'Tommy Production'
print(tt_key.name)

# Change Johnny's key access using update() method.  share_type, role, and subcalendar_permissions can only be updated by direct call of `update()` method, and cannot be set through property setter
jt_key.update(share_type='selected_subcalendars', subcalendar_permissions=myperms, role='mixed')
print(jt_key.as_dict)                                   # Inspect new Dictionary Values

# Find Bobby's Key by name
bt_keys = calendar.find_key_by_name('Bobby', exact_match=False, case_sensitive=False)       # Returns Tuple of matching values
if not bt_keys:
    print('No Key Found')
else:
    if len(bt_keys) > 1:
        print('Found More than 1 key')
    bt_key = bt_keys[0]

# Disable Johnny's key
print(jt_key.active)
jt_key.active = False 
print(jt_key.active)                                    

# Build a link for bobby
print(f'Bobby\'s Link is: https://teamup.com/{bt_key.key}')

# Delete Johnny's key
calendar.delete_key(jt_key.id)
```

## todo
 * Further refactor error handling to output the full error message provided by TeamUp 
 * Add support for updating recurring events
 * Build Subcalendar object with update support similar to Event object
 * Add Tests
 * Add more Event endpoints (get history, get auxilliary info)
 * Add More Calendar endpoints (searching for events)
 * Add Color Swatch Lookup (create simple assignments for red, blue, green, etc)
 * Add support for beta features: undo, custom fields, comments, signup

## Batch Mode
Events objects feature a batch mode for setting multiple values with a single api call, reducing your api usage and reducing the liklihood of TeamUp disabling your api key! Simply call `event.enable_batch_mode()` and begin making changes. When satisfied changes can be commited by calling `event.batch_commit()` which will automatically exit batch mode after, or call `event.disable_batch_mode(clear=True)` to discard changes. 

Setting event data without enabling batch mode will cause each change to use an api request. 

Note: there is no equivalent "batch" mode in the `Key` object, but you can pass all key arguments to the `update()` method to change multiple values in a single API call.

## Questions
Use issue tracker please :)

## FAQ
none

## Change Log  
**0.1.5a-ALPHA**  
Special Thanks to Frederick Schaller IV (@LogicallyUnfit on Github) for providing basis that this update was built off. Much of his code was re-used or refactored into this version release.

*Calendar Object*
* Added `key` property which returns the current Keys as a tuple (note: this always fetches the latest key data from the API, it is never stored)
* Added `get_key()` method and `get_key_collection()` method 
* Added `delete_key()` method
* Added `create_key()` method
* Added support for password protected access keys by adding `password` to the `__init__` of the Calendar, stored in header and used for every api call.
* Added Helper method `find_key_by_name` Supports, Case Sensitive, Exact Match. Returns tuple containing all matches (or empty tuple if No matches).
* Added Markdown support to `get_event_collection`
* Rewrote check_status_code to accept necessary arguments `url` and `headers` to use with `HTTPError` (further refactoring likely here)
* Refactored all Exceptions to be more descriptive allowing for better handling


*Key Object*
* Implemented Python Object for holding the `Key` data model as provided by the TeamUp API
* All values accessible via object properties
* Added setters for `name`, `active`, and `admin`
* Implemented `update()` method for bulk update, or for complex update such as changing permission sets, adding passwords, etc.
* Class variables `PERMISSIONS` `ROLES` and `SHARE_TYPES` hold valid values for respective key parameters

**0.1.4a**  
* Added basic support for `Event.attachment` property to `Event` class to fix new undocumented change to teamup api. (credit: LogicallyUnfit)


**0.1.3a**
* Refactored utilities `format_date` to use better timestamp awareness. 

**0.1.2a**
* Refactored date parameters in all object methods to use `dt` instead of `date` (requested by: LoreKeeperKen)
* Eliminated unnecessary reproduction of pandas `to_datetime` in favor of `dateutil`'s `parse` 
* Refactored check_status_code
* minor Pep8 adjustments
* fixed readme code errors

**0.1.1a**
* Fixed versioning
* Fixed file names, fixed import bug 

**0.1.0a2** 
* Added "get_changed_events" method to Calendar (credit: vranki)

**0.1.0a1** 
* Initial realease

## Contributors
Thank you to vranki for helping add features to the library, and LogicallyUnfit for helping keep the library stable during an undocumented API change, as well as their pull request which helped get Access Keys up and running!
 