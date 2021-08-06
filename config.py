
import configparser
import re
import location

cfg = configparser.ConfigParser(allow_no_value=True, strict=False,
                                inline_comment_prefixes=('#',))

cfg.read("example-data/conguide.cfg")

event_name = cfg.get('convention', 'convention')

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

session_initial_abbreviations = {}
session_continue_abbreviations = {}

for abbrev in cfg.items("session abbrev initial"):
    session_initial_abbreviations[abbrev[0]] = abbrev[1]

for abbrev in cfg.items("session abbrev continue"):
    session_continue_abbreviations[abbrev[0]] = abbrev[1]


