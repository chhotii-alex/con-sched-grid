#!/usr/bin/env python3

import math
import re
import bucket

'''
N.B. that we hard-code the assumption that there's only one date within
the event's time-frame with a given day of the week. Thus, handing events
of duration longer than a week would require non-trivial revision here.
This seems to be a limitation of Zambia (given that it reports 'day' as,
say, 'Fri'), so I'm not going to worry about this.
Generally these events start Friday (could conceivably have something on 
Thursday) and span a weekend. Note that if we had an event that spanned
Wednesday/Thursday, the day numbering here would have to be re-jiggered.
Ideally the date numbering would be data-driven. But,as  long as Zambia 
and conguide have this same limitation, I'm not going to
worry about that too much.
''' 
days = ['Thurday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']

day_number = {}
for i in range(len(days)):
    day = days[i]
    day_number[day[0:3]] = i

def ampm_str_to_minute(a_string):
    a_string = a_string.strip()
    m = re.match(r'(\d+):(\d+) +([AP]M)', a_string)
    if not m:
        raise Exception("Mal-formed time specification: " + a_string)
    hour = int(m.group(1))
    minute = int(m.group(2))
    if m.group(3) == 'AM':
        if hour == 12:
            hour = 0
    elif m.group(3) == 'PM':
        if hour < 12:
            hour += 12
    return hour*60+minute

def miltime_str_to_minute(a_string):
    a_string = a_string.strip()
    m = re.match(r'(\d+):(\d+)', a_string)
    if not m:
        raise Exception("Mal-formed time specification: " + a_string)
    hour = int(m.group(1))
    minute = int(m.group(2))
    return hour*60+minute

def duration_str_to_minutes(a_string):
    a_string = a_string.strip()
    parts = a_string.split(" ")
    result = 0
    for part in parts:
        if not len(part.strip()):
            continue
        m = re.match(r'(\d+)([a-z]+)', part)
        if not m:
            raise Exception("Mal-formed duration specification part: " + part)
        amount = int(m.group(1))
        if m.group(2) == 'hr':
            amount *= 60
        elif m.group(2) == 'min':
            pass
        else:
            raise Exception("I do not know what this time unit is here: " + part)
        result += amount
    return result

'''
N.B. that we are hard-coding in a couple of assumptions about
time ranges:
1) one time range must start at midnight;
2) each time range of the day is of equal length.
'''
class PageTimeRange:
    def __init__(self, name, start, end):
        self.name = name
        self.start = miltime_str_to_minute(start)
        self.end = miltime_str_to_minute(end)
        if self.end < self.start:
            self.end += 24*60
        self.minutes_per_box = 15
        self.minutes_per_label = 30

    def __repr__(self):
        return "%s to %s" % (self.time_string_for_min(self.start),
                             self.time_string_for_min(self.end) )

    def time_string_for_min(self, min):
        min = min % (24*60)
        if min == 0:
            return 'midnight'
        if min == 12*60:
            return 'noon'
        ampm = 'a'
        hour = math.floor(min/60)
        if hour >= 12:
            ampm = 'p'
        if hour == 0:
            hour = 12
        if hour > 12:
            hour -= 12
        minute = min % 60
        return "%d:%02d%s" % (hour, minute, ampm)

    def time_strings(self):
        results = []
        for min in range(self.start, self.end, self.minutes_per_label):
            results.append(self.time_string_for_min(min))
        return results

    def interval_count(self):
        return int((self.end-self.start)/self.minutes_per_box)

    def intervals_per_label(self):
        return int(self.minutes_per_label/self.minutes_per_box)

    def index_for_time(self, min):
        return int((min-self.start)/self.minutes_per_box)

    def intervals_for_duration(self, dur):
        return math.ceil(dur/self.minutes_per_box)

    def intervals_per_day(self):
        return int(24*60/self.minutes_per_box)

''' Create page time ranges (what conguide calls a "slice").'''
time_ranges = [PageTimeRange("Wee Hours", "1:30", "8:30"),
               PageTimeRange("Morning/Afternoon", "8:30", "17:30"),
               PageTimeRange("Evening", "17:30", "1:30") ]

class PageBucket(bucket.Bucket):
    def __init__(self, day, time_range):
        super().__init__()
        self.day = day
        self.time_range = time_range

class PageBucketArray(bucket.BucketArray):
    def make_buckets(self):
        for day in days:
            for time_range in time_ranges:
                yield PageBucket(day, time_range)

    def index_range_for_item(self, session):
        start_day_number = day_number[session.get_day()]
        day_bin = len(time_ranges)*start_day_number 
        day_bin -= 1;

        start_bin = day_bin
        for time_range in time_ranges:
            if session.get_time_minute_of_day() >= time_range.start:
                start_bin += 1

        end_bin = day_bin
        end_minutes = session.get_time_minute_of_day() + \
            session.get_duration() - 1
        while end_minutes > (24*60):
            end_minutes -= (24*60)
            end_bin += len(time_ranges)
        for time_range in time_ranges:
            if end_minutes >= time_range.start:
                end_bin += 1

        return (start_bin, end_bin)

def run_unit_tests():
    assert ampm_str_to_minute("6:00 AM") == 360
    assert ampm_str_to_minute("6:40 AM") == 400
    assert ampm_str_to_minute("12:00 AM") == 0
    assert ampm_str_to_minute("12:01 AM") == 1
    assert ampm_str_to_minute("12:00 PM") == 12*60
    assert ampm_str_to_minute("9:00 PM") == 21*60
    assert ampm_str_to_minute("11:59 PM") == (24*60-1)
    assert miltime_str_to_minute("00:00") == 0
    assert miltime_str_to_minute("00:01") == 1
    assert miltime_str_to_minute("00:41") == 41
    assert miltime_str_to_minute("12:00") == 12*60
    assert miltime_str_to_minute("21:00") == 21*60
    assert duration_str_to_minutes("15min") == 15
    assert duration_str_to_minutes("3hr") == 3*60
    assert duration_str_to_minutes("1hr 15min") == 75

if __name__ == "__main__":
    run_unit_tests()
