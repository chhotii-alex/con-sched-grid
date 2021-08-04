import os
from datetime import datetime, timezone
import csv
from session import Session

class Database:
    def __init__(self, file_name):
        self.file_name = file_name
        self.timestr = self.find_data_timestamp()

    def get_session_data(self):
        results = []
        # See https://discuss.codecademy.com/t/what-does-the-newline-argument-do/463575
        # for an explanation of why we use the newline argument when opening a file
        # for the csv module to read.
        fh = open(self.file_name, 'rt', encoding='utf-8', newline='')
        reader = csv.DictReader(fh)
        for row in reader:
            results.append(Session(row))
        fh.close()
        return results

    def get_data_timestamp(self):
        return self.timestr

    def find_data_timestamp(self):
        info = os.stat(self.file_name)
        modified = datetime.fromtimestamp(info.st_mtime, tz=timezone.utc)
        return modified.date().strftime("%d-%b")
