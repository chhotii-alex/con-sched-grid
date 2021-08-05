# con-sched-grid

Intended for producing a concise graphical summary of the schedule of, for example, a science fiction convention in a hotel.
This set of scripts will ingest a schedule listing (exported, for example, from https://github.com/olszowka/Zambia) and export HTML files containing schedule
grids formatted as tables.

*Requires* Python 3. I am not making the feeblest attempt at continuing to be backwards-compatible with Python 2.

To run, execute the main script using Python 3, i.e.:
`python3 main.py`
Currently the path to the input file is hard-coded as `example-data/pocketprogram.csv` and no command-line switches are supported. (To be improved in future
enhancements.) 
The script will create a set of HTML files in the current directory, containing the output. *On a Macintosh*, the script will cause these to be opened with your
default browser.

Note: At this point, if you wish to print the result (as opposed to *just* viewing in a browser), use Chrome. I'm using the non-standard CSS attribute
`-webkit-print-color-adjust: exact; ` and I've only tried this in Chrome.

## Data Model

A *Session* is a scheduled item, such as a panel discussion, lecture, demonstration, film screening, organized activity, theatrical performance, reception, etc.
Each Session has a name (*title*), a date and time, and a *Location* (and other attributes). 
The *Location* of a Session is given in the *room* column of the database table. The assumption is that this is for events held at a hotel, convention center, or
similar venue, which has a distinct set of named rooms for group events. Typically rooms are organized into groups (such as the levels of a hotel, or separate
venues for a very *large* convention); thus each room is associated with a *Level*. Rooms associated with the same Level are grouped together in the grid, to make
it easier for attendees to find things. The grids are organized with event location on the y axis and time on the x axis. Typically there is one event in a room 
at a time; if there is more than one, we assume that they start and end synchronously. 

The concept of a *Room* in a hotel turns out to be a bit more unruly and complicated than a distinct set of rooms, however, and the complications need to be 
reflected on the grid, where they occur. There are two types of complications to the basic *Room* concept:
1) Combination rooms; and
2) Multi-track rooms.

A *ComboRoom* occurs where a hotel has, for example, a large ballroom, which can be used in its entirety for large events, but can be divided into a number of
smaller rooms for smaller events using sliding temporary airwalls. For example, there may be a Grand Ballroom, which can be divided into Grand A, Grand B, and
Grand C. Typically you'll see small events broken out into Grand A, etc., during the day, and then in the evening the sliding walls are retracted for a large
event occupying all of Grand A/B/C. This is displayed on the grid by having separate rows for each of Grand A, B, and C, but then merging cells across rows 
to indicate the block of time where one event spans all three rooms. 

Multi-track rooms are rooms in which different activities may occur at opposite ends of the room, or at different tables, etc. We encapsulate the concept of 
parts of a room in the *Section* entity. Most rooms do not have any named sections, because they have one event at a time; in that case, asking a Room for its 
Sections returns a one-item list containing just the room itself. However, for example, Hancock is a larger room in the Westin Waterfront, in which Arisia 
organizes independent tracks of kids' programming at each end&mdash; encoded as Hancock-FastTrack1 and Hancock-FastTrack2 in the database. The distinction 
between Hancock-FastTrack1 and Hancock-FastTrack2 would not be useful to attendees for finding these events, but the timings of events at each end of the room
are sometimes not in synchrony. In the grid, therefore, two rows together, each displaying an independent track of activity, are labeled as *Hancock*.

The complexities of the Location relationships are not encoded in the database. What can be gleaned from the database is a plain list of names of locations at the
Room or Section level, but no clue as to grouping into Levels, nor the information regarding what rooms are actually Sections and what rooms they each belong to,
nor what rooms are actually ComboRooms and what rooms they combine. This information must be read in from a configuration file. I'm aiming for it to be the case
that the same configuration file can be used for both this and for conguide (for the production of the Pocket Program). 
