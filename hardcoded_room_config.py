from location import *
from functools import total_ordering

@total_ordering
class WestinLevel(Level):
    def __init__(self, name, floor, wing):
        self.floor = floor
        self.wing = wing
        super().__init__(name, "%d%s" % (floor, wing))

    def __eq__(self, other):
        if self.floor != other.floor:
            return False
        if self.wing != other.wing:
            return False
        return True

    def __lt__(self, other):
        if self.wing > other.wing:
            return True
        if self.wing == other.wing:
            if self.floor > other.floor:
                return True
        return False

# For now we are hard-coding the levels/rooms/etc.
# TO-DO: Definitely read in from config file before production!!!
w1 = WestinLevel("Concourse Level", 1, "W")
conf = WestinLevel("Conference Level", 3, "E")
e2 = WestinLevel("Lobby East", 2, "E")
w3 = WestinLevel("Mezzanine", 3, "W")
w2 = WestinLevel("Lobby West", 2, "W")

w3.add_room(Room('Alcott'))
w3.add_room(Room('Adams'))
w3.add_room(Room('Board Room'))
w3.add_room(Room('Bulfinch'))
w3.add_room(Room('Douglas'))
w3.add_room(Room('Faneuil'))
w3.add_room(Room('Hale'))
w3.add_room(Room('Pool'))

conf.add_room(Room('Burroughs'))
conf.add_room(Room('Griffin'))
conf.add_room(Room('Independence'))
conf.add_room(Room('Lewis'))
conf.add_room(Room('Carlton'))
conf.add_room(Room('Harbor Prefunction'))
conf.add_room(Room('Harbor Ballroom I', 'Gaming', 'Harbor I')).suppress()
h2 = conf.add_room(Room('Harbor Ballroom II-III', 'Harbor II-III'))

w2.add_room(Room("Otis"))
w2.add_room(Room("Paine"))
w2.add_room(Room("Quincy"))
w2.add_room(Room("Revere"))
w2.add_room(Room("Stone"))
hancock = Room("Hancock", 'Fast Track')
hancock.add_section("Hancock-FastTrack1")
hancock.add_section("Hancock-FastTrack2")
w2.add_room(hancock)
webster = w2.add_room(Room("Webster", 'Fast Track'))
webster.add_section("Webster-FastTrack3")
webster.add_section("Webster-FastTrack4")
w2.add_room(Room("Lobby"))

e2.add_room(Room("Marina 1"))
e2.add_room(Room("Marina 2"))
e2.add_room(Room("Marina 3"))
e2.add_room(Room("Marina 4"))

w1.add_room(Room("Grand Prefunction"))
a = Room("Grand Ballroom A", 'Events', "Grand A")
b = Room("Grand Ballroom B", 'Events', "Grand B")
c = Room("Grand Ballroom C", 'Events', "Grand C")
d = Room("Grand Ballroom D", 'Events', "Grand D")
ComboRoom("Grand Ballroom AB", a, b)
ComboRoom("Grand Ballroom CD", c, d)
w1.add_room(a)
w1.add_room(b)
w1.add_room(c)
w1.add_room(d)
w1.add_room(Room("Commonwealth Ballroom ABC", 'Events', "Commonwealth"))


