#!/usr/bin/env python3

from functools import total_ordering
import autosort

gLocationLookup = {}
gLevelList = autosort.AutoSortedArray()

@total_ordering
class Location:
    def __init__(self, name, short_name = None):
        global gLocationLookup
        if name in gLocationLookup:
            raise Exception("Duplicate location object: %s" % name)
        gLocationLookup[name] = self
        self.name = name
        if short_name:
            self.short_name = short_name
        else:
            self.short_name = name

    def __str__(self):
        return self.short_name

    def __repr__(self):
        return str(self)

    def get_short_name(self):
        return self.short_name

    def get_rooms(self):
        return [self]

    def __eq__(self, other):
        if self.name != other.name:
            return False
        return True

    def __lt__(self, other):
        if self.name < other.name:
            return True
        return False

    def __hash__(self):
        return hash(self.name)

class Section(Location):
    def __init__(self, room, name):
        super().__init__(name)
        self.room = room

    def set_used(self, flag):
        self.room.set_used(flag)

    def get_rooms(self):
        return self.room.get_rooms()

    def get_sections(self):
        return [self]

@total_ordering
class Room(Location):
    def __init__(self, name, usage="", short_name=None):
        super().__init__(name, short_name)
        self.level = None
        self.usage = usage
        self.is_used = False
        self.suppress_flag = False
        # Most rooms do not have named sections:
        self.sections = None
        # Most rooms do not take part in combinations:
        self.combos = []

    def set_level(self, level):
        self.level = level

    def get_level(self):
        return self.level

    def add_combo_membership(self, combo):
        self.combos.append(combo)

    def get_combos(self):
        return self.combos

    def suppress(self):
        self.suppress_flag = True

    def is_suppressed(self):
        return self.suppress_flag

    def add_section(self, section_name):
        s = Section(self, section_name)
        if not self.sections:
            self.sections = autosort.AutoSortedArray()
        self.sections.append(s)

    def set_used(self, flag):
        self.is_used = flag

    def should_display(self):
        return self.is_used and not self.is_suppressed()

    def get_used_sections(self):
        if self.sections:
            return self.sections
        else:
            return [self]

    def get_sections(self):
        return self.get_used_sections()

    def __lt__(self, other):
        all_combos = self.combos + other.get_combos()
        all_combos.sort()
        all_combos.reverse()
        for c in all_combos:
            if c not in self.combos:
                return True
            if c not in other.get_combos():
                return False
        if self.usage != other.usage:
            return self.usage < other.usage
        return self.name < other.name

@total_ordering
class Level(Location):
    def __init__(self, name, floor, wing, short_name=None):
        self.floor = floor
        self.wing = wing
        if short_name is None:
            short_name = "%d%s" % (floor, wing)
        super().__init__(name, short_name)
        global gLevelList
        gLevelList.append(self)
        self.rooms = autosort.AutoSortedArray()

    def add_room(self, room):
        self.rooms.append(room)
        room.set_level(self)
        return room

    def get_used_rooms(self):
        return [r for r in self.rooms if r.should_display()]

    def get_used_sections(self):
        results = []
        for r in self.get_used_rooms():
            results += r.get_used_sections()
        return results

    def __eq__(self, other):
        if self.floor != other.floor:
            return False
        if self.wing != other.wing:
            return False
        if self.name != other.name:
            return False
        return True

    def __lt__(self, other):
        if self.wing > other.wing:
            return True
        if self.wing == other.wing:
            if self.floor > other.floor:
                return True
            if self.floor == other.floor:
                return self.name < other.name
        return False
        
class ComboRoom(Location):
    def __init__(self, name, *args):
        super().__init__(name, None)
        self.rooms = []
        self.rooms.extend(args)
        self.rooms.sort()
        for r in self.rooms:
            if r.get_level():
                raise Exception("You must create ComboRooms BEFORE rooms are added to a Level.")
            r.add_combo_membership(self)

    def __repr__(self):
        return "Combo named " + self.name

    def set_used(self, flag):
        for room in self.rooms:
            room.set_used(flag)

    def get_rooms(self):
        return self.rooms

    def get_sections(self):
        return self.get_rooms()

def get_used_rooms():
    results = []
    for level in gLevelList:
        results += level.get_used_rooms()
    return results

def get_used_sections():
    results = []
    for level in gLevelList:
        results += level.get_used_sections()
    return results

def run_unit_tests():
    lev3 = Level("Level C", "foo")
    lev1 = Level("Level A", "bar")
    lev4 = Level("Level D", "baz")
    lev2 = Level("Level B", "bax")
    '''  The sorting rule for a Level is inherited from Location 
    unchanged: to wit, Levels are sorted alphabetically by full name.
    '''
    for i in range(1, len(gLevelList)):
        if gLevelList[i].name <= gLevelList[i-1].name:
            print(gLevelList[i-1], gLevelList[i].name)
            raise Exception("Whoa, sorting test for Level failed!")
    ernie = Room('Ernie')
    bert = Room('Bert')
    couple = ComboRoom("Ernie+Bert", ernie, bert)
    grover = Room('Grover')
    elmo = Room("Elmo")
    cookie = Room('Cookie Monster')
    monsters = ComboRoom("Monsters", grover, elmo, cookie)
    ''' N.B., we MUST create ComboRooms before the rooms are added to 
    the Level; otherwise the sorting won't work. '''
    lev1.add_room(ernie)
    lev1.add_room(bert)
    lev1.add_room(grover)
    lev1.add_room(elmo)
    lev1.add_room(cookie)
    lev1.add_room(Room('Snuffleupagus', 'Fast Track'))
    lev1.add_room(Room('Big Bird', 'Fast Track'))
    lev1.add_room(Room('Kermit', 'Artist Alley'))
    lev1.add_room(Room('Zoe'))
    ''' Test sorting for Rooms within a level. 
       A few factors override name in the sorting of rooms.
       1. Rooms that participate in Combos appear after rooms that don't.
       2. Rooms in the same ComboRoom must sort together.
       3. Rooms are sorted by (optional) usage first, then by name. 
    '''
    for i in range(1, len(lev1.rooms)):
        room = lev1.rooms[i]
        prev_room = lev1.rooms[i-1]
        if len(room.combos) < len(prev_room.combos):
            raise Exception("Room with combo first???")
        if room.combos and prev_room.combos:
            if room.combos[0].name < prev_room.combos[0].name:
                raise Exception("Sorting of the combos???")
        if len(room.combos) == len(prev_room.combos):
            if not room.combos or room.combos[0] == prev_room.combos[0]:
                if room.usage < prev_room.usage:
                    raise Exception("Incorrect sorting by usage???")
                elif room.usage == prev_room.usage:
                    if room.name < prev_room.name:
                        raise Exception("Incorrect sorting by name???")

if __name__ == "__main__":
    run_unit_tests()
