
import configparser
import re
import location

cfg = configparser.ConfigParser(allow_no_value=True, strict=False,
                                inline_comment_prefixes=('#',))

cfg.read("example-data/conguide.cfg")

event_name = cfg.get('convention', 'convention')

# Notice the differences between sections, grid rooms, and aliases:
# If grid rooms is specified, each grid room is labeled with its own
# name on its own row and when not merged, there is a border.
# For example Grand A + Grand B = Grand AB.
# If sections is specified, only one label is used, there is no border
# seperating the sections on the grid, but the row is double height
# (really two rows so each can have independent programming).
# For example Hancock consists of Hancock-FastTrack1 and Hancock-FastTrack2.
# If aliases are specified, they are really just aliases. One row is 
# generated with one label and everything goes into that row.
for section in cfg.sections():
    m = re.match(r'room (.*)', section)
    if m:
        name = m.group(1)
        try:
            pubsname = cfg.get(section, 'pubsname')
        except configparser.NoOptionError:
            pubsname = None
        try:
            usage = cfg.get(section, 'usage')
        except configparser.NoOptionError:
            usage = ""
        try:
            corners = cfg.get(section, 'sections')
            corners = re.split(r',\s*', corners)
        except configparser.NoOptionError:
            corners = []
        try:
            gridroom = cfg.get(section, 'grid room')
            room_names = re.split(r',\s*', gridroom)
            rooms = [location.gLocationLookup[r] for r in room_names]
            location.ComboRoom(name, rooms)
        except configparser.NoOptionError:
            room = location.Room(name, usage, pubsname)
            for c in corners:
                room.add_section(c)
        try:
            aliases = cfg.get(section, 'aliases')
            aliases = re.split(r',\s*', aliases)
            for al in aliases:
                location.gLocationLookup[al] = location.gLocationLookup[name]
        except configparser.NoOptionError:
            pass

for section in cfg.sections():
    m = re.match(r'(level|venue) (.*)', section)
    if m:
        name = m.group(2)
        pubsname = cfg.get(section, 'pubsname')
        floor = int(pubsname[0])
        wing = pubsname[1]
        level = location.Level(name, floor, wing)
        rooms = cfg.get(section, 'rooms')
        rnames = re.split(r',\s*', rooms)
        for rname in rnames:
            if rname not in location.gLocationLookup:
                location.Room(rname)
            level.add_room(location.gLocationLookup[rname])

# Use aliases on the room definition, because
# THIS DOES NOT WORK, because the case is smashed for the key:
#for mapping in cfg.items("session change room"):
#    location.gLocationLookup[mapping[0]] = location.gLocationLookup[mapping[1]]

print(location.gLocationLookup)

session_initial_abbreviations = {}
session_continue_abbreviations = {}

for abbrev in cfg.items("session abbrev initial"):
    session_initial_abbreviations[abbrev[0]] = abbrev[1]

for abbrev in cfg.items("session abbrev continue"):
    session_continue_abbreviations[abbrev[0]] = abbrev[1]


