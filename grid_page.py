import os
import threading, queue
from string import Template
import location
import bucket
import contime

css_template = '''
body {
  font-family: Arial, sans-serif;
}
.page-third {
  width: 33%;
  display: inline-block;
}
table {
 table-layout: fixed;
 border: 1px solid black;
}
td {
border: 1px solid black;
overflow: hidden;
}
table {
border-collapse: collapse;
}
.level-name {
 transform: rotate(-90deg);
 font-size: 10px;
 text-align: center;
}
.room-name {
 border: 1px solid black;
 text-align: right;
 font-size: 11px;
 width: ${w_unit4};
}
.first-room {
}
.just-black {
 background-color: black;
 -webkit-print-color-adjust: exact;
}
.no-border {
  border: 0;
}
.time-head {
 color: white;
 font-size: 9px;
 background-color: black;
 -webkit-print-color-adjust: exact;
}
.gray {
  background-color: #888888;
 -webkit-print-color-adjust: exact;
}
.schedule_item {
  font-family: 'Times New Roman', serif;
  font-size: 10px;
}
.event-name {
}
.page-title {
text-align: center;
font-weight: bold;
}
.version {
  text-align: right;
  font-size: 8px;
}
'''

main_template = '''
<!DOCTYPE html>
<html>
<head>
<style>
$css
</style>
<title>
$title
</title>
</head>
<body>
<div width="100%">
   <span class="page-third event-name" >
        $event
   </span>
   <span class="page-third page-title">
        $day $slice
   </span>
   <span class="page-third version">
        $zambia_ver
   </span>
</div>
$detail
</body>
</html>
'''

class Placeholder:
    def __init__(self, session):
        self.session = session

    def is_placeholder(self):
        return True

    def get_time_minute_of_day(self):
        return self.session.get_time_minute_of_day()

    def get_duration(self):
        return self.session.get_duration()

class TimeSlotBucketArray(bucket.BucketArray):
    def __init__(self, time_range):
        self.time_range = time_range
        super().__init__()

    def make_buckets(self):
        for _ in range(self.time_range.interval_count()):
            yield bucket.Bucket()

    def index_range_for_item(self, session):
        start_bucket_number = self.time_range.index_for_time(
            session.get_time_minute_of_day())
        end_bucket_number = self.time_range.index_for_time(
            session.get_time_minute_of_day() + session.get_duration() - 1)
        # Session may have started before start of time range... on 
        # previous day!
        while start_bucket_number >= self.time_range.interval_count():
            start_bucket_number -= self.time_range.intervals_per_day()
            end_bucket_number -= self.time_range.intervals_per_day()
        # Session may have started before start of time range.
        if start_bucket_number < 0:
            start_bucket_number = 0
        # Session may go beyond this page's time
        if end_bucket_number >= self.time_range.interval_count():
            end_bucket_number = self.time_range.interval_count() - 1
        return (start_bucket_number, end_bucket_number)

    def get_schedule(self):
        prev_bucket = None
        schedule = []
        for bucket in self.buckets:
            if prev_bucket is not None and bucket.contains_same_contents(prev_bucket):
                schedule[-1][0] += 1
            else:
                schedule.append( [1, bucket.get_items()] )
            prev_bucket = bucket
        return schedule

class RowDetailThread(threading.Thread):
    def __init__(self, q, bucket_list, interval_max):
        super().__init__()
        self.q = q
        self.bucket_list = bucket_list
        self.interval_max = interval_max
        
    def get_detail_for_section(self, bucket_list, interval_max):
        results = ''
        curr_interval = 0
        for interval, sessions in bucket_list.get_schedule():
            if sessions and sessions[0].is_placeholder():
                continue
            if sessions:
                class_name = 'schedule_item'
            else:
                class_name = 'gray'
            if curr_interval + interval >= interval_max:
                interval = interval_max - curr_interval
            room_count = 1
            if sessions:
                room_count = sessions[0].get_room_count()
            results += '<td class="%s" colspan="%d" rowspan="%d">' % (
                class_name, interval, room_count)
            results += '<div class="limit-%dcol limit-%drow">' % (
                interval, room_count)
            results += '; '.join([s.get_title() for s in sessions])
            results += '</div></td>'
            curr_interval += interval
        return results

    def run(self):
        results = self.get_detail_for_section(self.bucket_list, 
                                              self.interval_max)
        self.q.put(results)
        return

class GridPage:
    def __init__(self, day_name, time_range, sessions):
        self.connection_dictionary = None
        self.cell_height = 21
        self.cell_width = 26
        self.day_name = day_name
        self.time_range = time_range
        self.sessions_per_section = {}
        for section in location.get_used_sections():
            self.sessions_per_section[section] = TimeSlotBucketArray(
                time_range)
        for session in sessions:
            first = True
            for section in session.get_sections():
                if section in self.sessions_per_section:
                    if first:
                        self.sessions_per_section[section].add_item(session)
                        first = False
                    else:
                        self.sessions_per_section[section].add_item(
                            Placeholder(session))

    def get_file_name(self):
        return "%s%s.html" % (self.day_name[0:3], self.time_range.name[0:3])

    def get_title(self):
        return "Grid for %s %s" % (self.day_name, self.time_range.name)

    def prime_detail_for_section(self, section):
        if self.connection_dictionary is None:
            self.connection_dictionary = {}
        if section in self.connection_dictionary:
            return
        bucket_list = self.sessions_per_section[section]
        interval_max = self.time_range.interval_count()
        q = queue.Queue() 
        thread = RowDetailThread(q, bucket_list, interval_max)
        thread.start()
        self.connection_dictionary[section] = q

    def get_detail_for_section(self, section):
        self.prime_detail_for_section(section)
        q = self.connection_dictionary[section]
        results = q.get()
        q.task_done()
        self.connection_dictionary.pop(section, None)
        return results

    def get_table_rows(self):
        rows = '''
        <table>
        '''
        rows += '''<tr>
        <td colspan="2" width="200px" class="no-border"></td>
        '''
        for _ in range(self.time_range.interval_count()):
            rows += '''<td colspan="1" class="limit-1col just-black"> </td>
                 '''
        rows += '</tr>'
        rows += '''
        <tr>
        <td colspan="2" width="200px" class="no-border" ></td>
        '''
        for time_str in self.time_range.time_strings():
            rows += '<td class="time-head limit-%dcol" colspan="%d">' % (
                self.time_range.intervals_per_label(),
                self.time_range.intervals_per_label())
            rows += '<div class="time-head">'
            rows += time_str
            rows += '''</div></td>
                  '''
        rows += '''
        </tr>
        <tbody>
        '''
        for level in location.gLevelList:
            for room in level.get_used_rooms():
                for section in room.get_sections():
                    self.prime_detail_for_section(section)
        for level in location.gLevelList:
            rooms = level.get_used_rooms()
            for room_index in range(len(rooms)):
                room = rooms[room_index]
                sections = room.get_sections()
                for section_index in range(len(sections)):
                    section = sections[section_index]
                    rows += '<tr>'
                    if room_index == 0:
                        rows += '<td rowspan="%d" class="limit-%drow">' % (
                            len(level.get_used_sections()), len(rooms))
                        rows += '<div class="level-name" width="20px">'
                        rows += level.name
                        rows += " (%s)" % level.short_name
                        rows += '</div>'
                        rows += '</td>'
                    if section_index == 0:
                        if room_index == 0:
                            class_string = 'first_room'
                        else:
                            class_string = ''
                        rows += '<td class="room-name %s" rowspan="%d">' % (
                            class_string, len(room.get_sections()))
                        rows += '<div limit_%drow">' % (
                            len(room.get_sections()))
                        rows += str(room)
                        rows += '</div></td>'
                    rows += self.get_detail_for_section(section)
                    rows += '</tr>\n'
        rows += '''
        </tbody>
        </table>
        '''
        return rows

    def write(self):
        fh = open(self.get_file_name(), 'wt')
        css = Template(css_template)
        sizes_dict = {}
        for i in range(12):
            sizes_dict['w_unit%d' % i] = '%dpx' % (i*self.cell_width)
            sizes_dict['h_unit%d' % i] = '%dpx' % (i*self.cell_height)
        css = css.substitute(sizes_dict)
        for i in range(1, 5):
            css += '''
             .limit-%drow { 
                overflow: hidden;
                max-height: %dpx;
                height: %dpx;
             }
             ''' % (i, self.cell_height*i, self.cell_height*i)
        for i in range(1, 13):
            css += '''
             .limit-%dcol { 
                overflow: hidden;
                max-width: %dpx;
                width: %dpx;
             }
             ''' % (i, self.cell_width*i, self.cell_width*i)
        contents = Template(main_template)
        contents = contents.substitute(title=self.get_title(),
                                       day=self.day_name,
                                       slice=self.time_range.name,
                                       detail=self.get_table_rows(),
                                       css=css,
                                       zambia_ver="preliminary", # TODO
                                       event="Arisia 2020" # TODO; hardcode for now
                                       )
        fh.write(contents)
        fh.close()

    # Convenience function: Show us the work when it's done. Only 
    # known to work on Macintosh.
    def open(self):
        os.system('open "%s"' % self.get_file_name())
