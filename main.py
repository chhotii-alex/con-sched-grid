#!/usr/bin/env python3

import math
import sys
import threading
from location import *
import hardcoded_room_config
from contime import *
from grid_page import *
import db_fetch

class PageBuildingThread(threading.Thread):
    def __init__(self, day, time_range, bucket):
        super().__init__()
        self.day = day
        self.time_range = time_range
        self.bucket = bucket

    def run(self):
        page = GridPage(self.day, self.time_range, self.bucket)
        page.write()
        page.open()
        

''' Create a time bucket to hold sessions in each slice of each day.
'''
page_content_buckets = [ [] for i in range(len(time_ranges)*len(days)) ]

for session in db_fetch.get_session_data():
    if session.is_included_in_grid():
        session.get_location().set_used(True)
        for page_number in range(session.first_page_number(), 
                                 session.last_page_number()+1):
            page_content_buckets[page_number].append(session)

for day_index in range(len(days)):
    day = days[day_index]
    for tr_index in range(len(time_ranges)):
        time_range = time_ranges[tr_index]
        bucket = page_content_buckets[day_index*len(time_ranges)+tr_index]
        if not bucket:
            continue # skip pages that would be totally empty
        thread = PageBuildingThread(day, time_range, bucket)
        thread.start()
