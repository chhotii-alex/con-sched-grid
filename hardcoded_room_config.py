from location import *

# For now we are hard-coding the levels/rooms/etc.
# TO-DO: Definitely read in from config file before production!!!
w3 = Level("Mezzanine", "3W")
w2 = Level("Lobby West", "2W")
w1 = Level("Concourse Level", "1W")
conf = Level("Conference Level", "3E")
e2 = Level("Lobby East", "2E")

w3.add_room('Alcott')
w3.add_room('Adams')
w3.add_room('Board Room')
w3.add_room('Bulfinch')
w3.add_room('Douglas')
w3.add_room('Faneuil')
w3.add_room('Hale')
w3.add_room('Pool')

conf.add_room('Burroughs')
conf.add_room('Griffin')
conf.add_room('Independence')
conf.add_room('Lewis')
conf.add_room('Carlton')
conf.add_room('Harbor Prefunction')
conf.add_room('Harbor Ballroom I', 'Harbor I').suppress()
h2 = conf.add_room('Harbor Ballroom II-III', 'Harbor II-III')

w2.add_room("Otis")
w2.add_room("Paine")
w2.add_room("Quincy")
w2.add_room("Revere")
w2.add_room("Stone")
hancock = w2.add_room("Hancock")
hancock.add_section("Hancock-FastTrack1")
hancock.add_section("Hancock-FastTrack2")
webster = w2.add_room("Webster")
webster.add_section("Webster-FastTrack3")
webster.add_section("Webster-FastTrack4")
w2.add_room("Lobby")

e2.add_room("Marina 1")
e2.add_room("Marina 2")
e2.add_room("Marina 3")
e2.add_room("Marina 4")

w1.add_room("Grand Prefunction")
a = w1.add_room("Grand Ballroom A", "Grand A")
b = w1.add_room("Grand Ballroom B", "Grand B")
c = w1.add_room("Grand Ballroom C", "Grand C")
d = w1.add_room("Grand Ballroom D", "Grand D")
ComboRoom("Grand Ballroom AB", a, b)
ComboRoom("Grand Ballroom CD", c, d)
w1.add_room("Commonwealth Ballroom ABC", "Commonwealth")


