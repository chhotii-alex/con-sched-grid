gLocationLookup = {}
gLevelList = []

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

    def get_level(self):
        raise Exception("Abstract method not defined")

    def get_rooms(self):
        return [self]

class Section(Location):
    def __init__(self, room, name):
        super().__init__(name)
        self.room = room

    def get_level(self):
        return self.room.get_level()

    def set_used(self, flag):
        self.room.set_used(flag)

    def get_rooms(self):
        return self.room.get_rooms()

class Room(Location):
    def __init__(self, level, name, short_name=None):
        super().__init__(name, short_name)
        self.level = level
        self.is_used = False
        self.suppress_flag = False
        # Most rooms do not have named sections:
        self.sections = None        

    def suppress(self):
        self.suppress_flag = True

    def is_suppressed(self):
        return self.suppress_flag

    def add_section(self, section_name):
        s = Section(self, section_name)
        if not self.sections:
            self.sections = []
        self.sections.append(s)

    def get_level(self):
        return self.level

    def set_used(self, flag):
        self.is_used = flag

    def should_display(self):
        return self.is_used and not self.is_suppressed()

class Level(Location):
    def __init__(self, name, short_name=None):
        super().__init__(name, short_name)
        global gLevelList
        gLevelList.append(self)
        self.rooms = []

    def add_room(self, room_name, room_short_name=None):
        room = Room(self, room_name, room_short_name)
        self.rooms.append(room)
        return room

    def get_level(self):
        return self

    def get_used_rooms(self):
        return [r for r in self.rooms if r.should_display()]
        
class ComboRoom(Location):
    def __init__(self, name, *args):
        super().__init__(name, None)
        self.rooms = args

    def get_level(self):
        return self.rooms[0].get_level()

    def set_used(self, flag):
        for room in self.rooms:
            room.set_used(flag)

    def get_rooms(self):
        return self.rooms

def get_used_rooms():
    results = []
    for level in gLevelList:
        results += level.get_used_rooms()
    return results
