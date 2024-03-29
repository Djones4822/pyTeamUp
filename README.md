# pyTeamUp
Python API wrapper for TeamUp API. In early stages, only has event and calendar objects implemented. 

**version**: 0.1.4a 

**Note**: version 0.1.4a is required for working with the TeamUp API as of 11/26/2021. This version adds basic support for `atttachment` event attribute, but  since it is undocumented in the official API there is no way to add or remove attachments. They can be viewed using `event.attachments` if set through the Web interface.

## Installation
python 3.6 or higher required. Use pip (Current Version: 0.1.4a):
```
python -m pip install pyTeamUp
```

## Features:
 * Pythonic access to TeamUp calendars and events.
 * Simple interface for gathering subcalendars and event containers. 
 * Simple interface for creating and deleting events with `Calendar` object
 * `Event` Object features simple interface for updating event properties 
 * Batch mode for reducing api calls for updating multiple event properties
 * If pandas is present, Calendar can return events as Series objects and event collections as DataFrame objects
 
## Example usage
```python
from pyteamup import Calendar, Event
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
print(evnt.is_deleted)                         # Will return True
```

## todo
 * Add support for updating recurring events
 * Build Subcalendar object with update support similar to Event object
 * Add Tests
 * Add more Event endpoints (get history, get auxilliary info)
 * Add More Calendar endpoints (searching for events)
 * Add Access Key Endpoints
 * Add Color Swatch Lookup (create simple assignments for red, blue, green, etc)
 * Add support for password protected calendars
 * Add support for beta features: undo, custom fields, comments, signup


## Batch Mode
Events objects feature a batch mode for setting multiple values with a single api call, reducing your api usage and reducing the liklihood of TeamUp disabling your api key! Simply call `event.enable_batch_mode()` and begin making changes. When satisfied changes can be commited by calling `event.batch_commit()` which will automatically exit batch mode after, or call `event.disable_batch_mode(clear=True)` to discard changes. 

Setting event data without enabling batch mode will cause each change to use an api request. 

## Questions
Use issue tracker please :)

## FAQ
none

## Change Log  
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
Thank you to vranki for helping add features to the library, and LogicallyUnfit for helping keep the library stable during an undocumented API change. 
 