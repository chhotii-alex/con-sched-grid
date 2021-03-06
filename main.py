#!/usr/bin/env python3

import math
import sys
from location import *
import config
from contime import *
from grid_page import *
import db_fetch

class PageBuilder:
    def __init__(self, bucket):
        self.day = bucket.day
        self.time_range = bucket.time_range
        self.sessions = bucket.items
        self.page = None

    def make_page(self, page_number, timestr):
        self.page = GridPage(self.day, self.time_range, self.sessions, 
                             page_number, timestr)
        self.page.write()
        self.page.open()


class GridMaker:
    def __init__(self):
        self.contents = None
        self.db = db_fetch.Database("example-data/pocketprogram.csv")

    def prep_data(self):
        ''' Create a time bucket to hold sessions in each slice of each day.
        '''
        self.contents = PageBucketArray()

        for session in self.db.get_session_data():
            if session.is_included_in_grid():
                session.get_location().set_used(True)
                self.contents.add_item(session)

    def make_grids(self):
        self.prep_data()

        page_number = 1
        for bucket in self.contents.get_buckets():
            if not bucket.is_empty():
                builder = PageBuilder(bucket)
                builder.make_page(page_number, self.db.get_data_timestamp())
                page_number += 1

        print("Done!")

if __name__ == "__main__":
    my_grid_maker = GridMaker()
    my_grid_maker.make_grids()

