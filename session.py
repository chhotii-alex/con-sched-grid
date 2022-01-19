from functools import total_ordering
from contime import *
from location import *
import config
import cleaner

@total_ordering
class Session:
    def __init__(self, data):
        self.id = data['sessionid']
        self.day = data['day']
        self.time = data['time']
        self.duration = duration_str_to_minutes(data['duration'])
        self.location = gLocationLookup[data['room']]
        self.title = data['title']
        (self.title, _) = cleaner.clean_tags(self.title, ['i'])
        # We have other info on each session, but it's ignored for the
        # purpose of a grid.

    def is_placeholder(self):
        return False

    def __str__(self):
        return "'%s' on %s at %s, for %d minutes" % (
            self.title, self.day, self.time, self.duration)

    def get_title(self):
        return self.title

    def get_abbreviation(self):
        if self.id in config.session_initial_abbreviations:
            return config.session_initial_abbreviations[self.id]
        else:
            return self.get_title()

    def get_continuation_abbrev(self):
        if self.id in config.session_continue_abbreviations:
            return config.session_continue_abbreviations[self.id]
        else:
            return self.get_title()

    def get_location(self):
        return self.location

    def get_level(self):
        return self.get_location().get_level()

    ''' Returns an array. May contain more than one item, if the
    location is a Combo Room. '''
    def get_rooms(self):
        return self.get_location().get_rooms()

    def get_sections(self):
        return self.get_location().get_sections()

    def get_room_count(self):
        return len(self.get_rooms())

    def get_day(self):
        return self.day

    def get_start_day_number(self):
        return day_number[self.day]
    
    def get_time_str(self):
        return self.time.replace(" ", "").lower()

    def get_time_minute_of_day(self):
        return ampm_str_to_minute(self.time)

    def get_duration(self):
        return self.duration

    # TO-DO: add more ways to make this data-driven
    def is_included_in_grid(self):
        return self.duration > 0 and \
            all(not r.is_suppressed() for r in self.get_rooms())

    def __key(self):
        return (day_number[self.day],
                self.get_time_minute_of_day(),
                self.get_duration(),
                str(self.get_location()),
                self.get_title() )

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Session):
            result = self.__key() == other.__key()
            return result
        return False

    def __lt__(self, other): 
        if isinstance(other, Session):
            return self.__key() < other.__key()
        else:
            return True
