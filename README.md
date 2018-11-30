# pyTeamUp
Python API wrapper for TeamUp API. In early stages, only has event and calendar objects implemented. 

**version**: 0.1.0a

## Features:
 * Pythonic access to TeamUp calendars and events.
 * Simple interface for gathering subcalendars and event containers. Can also create an event by passing an event ID.
 * Event Object features simple interface for updating event properties 
 * Batch mode for reducing api calls for updating multiple event properties
 * If pandas is present, Calendar can return events as Series objects and event collections as DataFrame objects

## todo
 * Add better support for creating an event
 * Add support for updating recurring events
 * Build Subcalendar object with update support similar to Event object
 * Add Event Delete Support 
 * Add support for undo (api returns undo id, not sure what this is!)
 * Make a release available on pip

## Installation
*coming soon*

##Batch Mode
Events objects feature a batch mode for setting multiple values with a single api call, reducing your api usage and reducing the liklihood of TeamUp disabling your api key! Simply call `event.enable_batch_mode()` and begin making changes. When satisfied changes can be commited by calling `event.batch_commit()` which will automatically exit batch mode after, or call `event.disable_batch_mode(clear=True)` to discard changes. 

Setting event data without enabling batch mode will cause each change to use an api request. 

## Questions
Use issue tracker please :)

## FAQ
none
