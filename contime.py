
import math
import re

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
        self.start = int(start)
        self.end = int(end)
        self.minutes_per_box = 15
        self.minutes_per_label = 30

    def time_string_for_min(self, min):
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

time_range_names = ["Wee Hours",
                    "Morning/Afternoon",
                    "Evening"]
time_ranges_per_day = len(time_range_names)

minutes_per_time_range = 24*60/len(time_range_names)

''' Create page time ranges (what conguide calls a "slice").
Each is 8 hours, starting at midnight, 8 am, and 4 pm. '''
time_ranges = [PageTimeRange(time_range_names[i], 
                             minutes_per_time_range*i, 
                             minutes_per_time_range*(i+1)) 
          for i in range(time_ranges_per_day)]

class PageBucket:
    def __init__(self, day, time_range):
        self.day = day
        self.time_range = time_range
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def is_empty(self):
        return len(self.items) == 0

class PageBucketArray:
    def __init__(self):
        self.buckets = []
        for day in days:
            for time_range in time_ranges:
                self.buckets.append(PageBucket(day, time_range))

    def start_index_for_item(self, session):
        start_day_number = day_number[session.get_day()]
        result = len(time_range_names)*start_day_number 
        result += math.floor(
            session.get_time_minute_of_day()/minutes_per_time_range)
        return result
        
    def end_index_for_item(self, session):
        end_minutes = session.get_time_minute_of_day() + \
            session.get_duration() - 1
        start_day_number = day_number[session.get_day()]
        result = len(time_range_names)*start_day_number 
        result += math.floor(end_minutes/minutes_per_time_range)
        return result        

    def add_item(self, session):
        first_bucket_number = self.start_index_for_item(session)
        last_bucket_number = self.end_index_for_item(session)
        for bucket_number in range(first_bucket_number,
                                 last_bucket_number+1):
            self.buckets[bucket_number].add_item(session)

    def get_buckets(self):
        return self.buckets
