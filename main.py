#!/usr/bin/env python3

import math
import sys
from location import *
import hardcoded_room_config
from contime import *
from grid_page import *
import db_fetch

''' Create a time bucket to hold sessions in each slice of each day.
'''
page_content_buckets = [ [] for i in range(len(time_ranges)*len(days)) ]

for session in db_fetch.get_session_data():
    if session.is_included_in_grid():
        session.get_location().set_used(True)
        page_content_buckets[session.page_number()].append(session)

for day_index in range(len(days)):
    day = days[day_index]
    for tr_index in range(len(time_ranges)):
        time_range = time_ranges[tr_index]
        bucket = page_content_buckets[day_index*len(time_ranges)+tr_index]
        if not bucket:
            continue # skip pages that would be totally empty
        page = GridPage(day, time_range, bucket)
        page.write()
        page.open()
