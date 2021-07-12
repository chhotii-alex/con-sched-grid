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
    def __init__(self, bucket):
        super().__init__()
        self.day = bucket.day
        self.time_range = bucket.time_range
        self.sessions = bucket.items

    def run(self):
        page = GridPage(self.day, self.time_range, self.sessions)
        page.write()
        page.open()
        

''' Create a time bucket to hold sessions in each slice of each day.
'''
contents = PageBucketArray()

for session in db_fetch.get_session_data():
    if session.is_included_in_grid():
        session.get_location().set_used(True)
        contents.add_item(session)

threads = []
for bucket in contents.get_buckets():
    if not bucket.is_empty():
        thread = PageBuildingThread(bucket)
        thread.start()
        threads.append(thread)

for thread in threads:
    thread.join()
print("Done!")
