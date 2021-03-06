import os
import math
from string import Template
from functools import total_ordering
import autosort
import location
import bucket
import contime
import config

css_template = '''
body {
  font-family: Arial, sans-serif;
}
.grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: auto;
  grid-template-areas:
    "event slice zambia"
    "table table table";
}
table {
 table-layout: fixed;
 border: 0.01in solid black;
 border-collapse: collapse;
}
td {
  border: 0.01in solid black; 
  padding: 0.01in; 
overflow: hidden;
}
.level-name {
 border-style: solid;
 border-width: 0.01in;
 border-color: black Gray black black;
 z-index: -1;
 text-align: center;
 white-space: nowrap;
 vertical-align: middle;
 width: ${w_unit2};
}
.level-name div {
 transform: rotate(-90deg);
 font-size: 10px;
 margin-left: -6em;
 margin-right: -6em;
}
.room-name {
 border-style: solid;
 border-width: 0.01in;
 border-color: Gray black Gray Gray;
 z-index: -1;
 text-align: right;
 font-size: 11px;
 width: ${w_unit4};
}
.first_room {
 border-color: black black Gray Gray;
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
  grid-area: event;
}
.page-title {
  text-align: center;
  font-weight: bold;
  grid-area: slice;
}
.version {
  text-align: right;
  font-size: 8px;
  grid-area: zambia;
}
.table {
  grid-area: table;
  /* overflow: hidden; */
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
<div class="table-width grid-container" >
   <span class="event-name" >
        $event
   </span>
   <span class="page-title">
        $day $slice
   </span>
   <span class="version">
        $zambia_ver
   </span>

   <div class="table" >
     $theader
     $detail
     $tfoot
   </div>
</div>
$bottom
</body>
</html>
'''

class Placeholder:
    def __init__(self, session):
        self.session = session

    def is_placeholder(self):
        return True

    def get_title(self):
        return self.session.get_title()

    def get_abbreviation(self):
        return self.session.get_abbreviation()

    def get_continuation_abbrev(self):
        return self.session.get_continuation_abbrev()

    def get_time_minute_of_day(self):
        return self.session.get_time_minute_of_day()

    def get_duration(self):
        return self.session.get_duration()

    def get_start_day_number(self):
        return self.session.get_start_day_number()

    def get_room_count(self):
        return self.session.get_room_count()

    def get_time_str(self):
        return self.session.get_time_str()

    def __repr__(self):
        return "placeholder for %s" % (self.session)

@total_ordering
class SessionOverlapperWrapper:
    def __init__(self, session):
        self.session = session

    def is_placeholder(self):
        return self.session.is_placeholder()

    def get_abbreviation(self):
        return "<i>%s</i> %s" % (self.session.get_time_str(), 
                                 self.session.get_continuation_abbrev() )

    def get_time_minute_of_day(self):
        return self.session.get_time_minute_of_day()

    def get_duration(self):
        return self.session.get_duration()
        
    def get_room_count(self):
        return self.session.get_room_count()

    def __eq__(self, other):
        if isinstance(other, SessionOverlapperWrapper):
            return self.session == other.session
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, SessionOverlapperWrapper):
            return self.session < other.session
        else:
            return False

class TimeSlotBucketArray(bucket.BucketArray):
    def __init__(self, time_range, day_number):
        self.time_range = time_range
        self.day_number = day_number
        super().__init__()

    def make_buckets(self):
        for _ in range(self.time_range.interval_count()):
            yield bucket.Bucket(autosort.AutoSortedArray())

    def overlapper_wrapper_for_item(self, item):
        return SessionOverlapperWrapper(item)

    '''
       Return the start and end indexes of times slots occupied (within this page)
       by the given session.
       If there's a mismatch between the session's given day and my day, this
       is due to something spanning midnight (either a session or a time range),
       and a correction for the day has to be applied.
       The starting index might be less than 0, or the end index might be past
       the end of the array-- that's expected, when the session overlaps an edge of
       this page's time slice. That's fine-- BucketArray.add_item() knows to trim 
       off the invalid indices from the ends.
    '''
    def index_range_for_item(self, session):
        start_minute = session.get_time_minute_of_day()
        end_minute = start_minute + session.get_duration() - 1
        if self.day_number > session.get_start_day_number():
            '''Session actually started last night. Shift range into frame.'''
            start_minute -= 24*60
            end_minute -= 24*60
        if self.day_number < session.get_start_day_number():
            ''' I overlap into next day, and this session starts after midnight.'''
            start_minute += 24*60
            end_minute += 24*60
        start_bucket_number = self.time_range.index_for_time(start_minute)
        end_bucket_number = self.time_range.index_for_time(end_minute)

        return (start_bucket_number, end_bucket_number)

    def get_schedule(self):
        prev_bucket = None
        schedule = []
        for bucket in self.buckets:
            if prev_bucket is not None and bucket.contains_same_contents(prev_bucket):
                schedule[-1][0] += 1
            else:
                schedule.append( [1, bucket] )
            prev_bucket = bucket
        return schedule

class RowDetailMaker:
    def __init__(self, bucket_list, interval_max):
        self.bucket_list = bucket_list
        self.interval_max = interval_max
        
    def get_cells_for_section(self):
        results = ''
        curr_interval = 0
        for interval, sessions in self.bucket_list.get_schedule():
            if sessions and sessions[0].is_placeholder():
                continue
            if sessions:
                class_name = 'schedule_item'
            else:
                class_name = 'gray'
            if curr_interval + interval >= self.interval_max:
                interval = self.interval_max - curr_interval
            room_count = 1
            if sessions:
                room_count = sessions[0].get_room_count()
            results += '<td class="%s" colspan="%d" rowspan="%d">' % (
                class_name, interval, room_count)
            results += '<div class="limit-%dcol limit-%drow">' % (
                interval, room_count)
            results += '; '.join([s.get_abbreviation() for s in sessions])
            results += '''</div></td>
            '''
            curr_interval += interval
        return results

class GridPage:
    def __init__(self, day_name, time_range, sessions, page_number, version):
        self.day_name = day_name
        self.time_range = time_range
        self.sessions_per_section = {}
        self.page_number = page_number
        self.version = version
        for section in location.get_used_sections():
            self.sessions_per_section[section] = TimeSlotBucketArray(
                time_range, contime.day_number_for_day_name(day_name))
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

    def get_detail_for_section(self, section):
        bucket_list = self.sessions_per_section[section]
        interval_max = self.time_range.interval_count()
        r = RowDetailMaker(bucket_list, interval_max)
        return r.get_cells_for_section()

    def get_cell_width(self):
        return self.get_table_width()/(6+self.time_range.interval_count()) - 0.04

    def get_cell_height(self):
        return self.get_table_height()/(1+self.get_row_count())

    '''Now in inches'''
    def get_table_width(self):
        return 10.0

    def get_table_height(self):
        return 7.0

    def get_table_header(self):
        rows = '''
        <table class="table-width">
          <thead>
        '''
        rows += '''<tr>
        <td colspan="1" class="no-border limit-2col"></td>
        <td colspan="1" class="no-border limit-4col"></td>
        '''
        for _ in range(self.time_range.interval_count()):
            rows += '''<td colspan="1" class="limit-1col just-black"> </td>
                 '''
        rows += '</tr>'
        rows += '''
        <tr>
        <td colspan="1" class="no-border limit-2col"></td>
        <td colspan="1" class="no-border limit-4col"></td>
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
          </thead>
        <tbody>
        '''
        return rows

    def get_row_start(self, level, room, section, is_1st_room, 
                      is_1st_section):
        results = '<tr>'
        if is_1st_room and is_1st_section:
            results += '<td rowspan="%d" class="level-name">' % (
                len(level.get_used_sections()) )
            results += '<div>'
            results += level.name
            results += "<br/>(%s)" % level.get_short_name()
            results += '</div>'
            results += '''</td>
             '''
        if is_1st_section:
            if is_1st_room:
                class_string = 'first_room'
            else:
                class_string = ''
            results += '<td class="room-name %s limit-4col" rowspan="%d">' % (
                class_string, len(room.get_sections()))
            results += '<div limit_%drow">' % (
                len(room.get_sections()))
            results += str(room)
            results += '''</div></td>
            '''
        return results

    def get_row_end(self):
        return '''</tr>
               '''

    # TODO: use a generator function to yield sections,
    # and refactor this function and the next to use it
    def get_table_rows(self):
        rows = ''
        for level in location.gLevelList:
            rooms = level.get_used_rooms()
            for room_index in range(len(rooms)):
                room = rooms[room_index]
                sections = room.get_sections()
                for section_index in range(len(sections)):
                    section = sections[section_index]
                    rows += self.get_row_start(level, room, section,
                                               (room_index == 0),
                                               (section_index == 0))
                    rows += self.get_detail_for_section(section)
                    rows += self.get_row_end()
        return rows

    def get_row_count(self):
        total = 0
        for level in location.gLevelList:
            rooms = level.get_used_rooms()
            for room_index in range(len(rooms)):
                room = rooms[room_index]
                sections = room.get_sections()
                total += len(sections)
        return total

    def get_table_foot(self):
        return '''
        </tbody>
        </table>
        '''

    def get_page_bottom(self):
        if False: 
            # I don't know why I had "page numbers" in my to-do list, this
            # is of questionable usefulness
            return '<div align="center">Page %d</div>' % (self.page_number)
        return ''

    def write(self):
        fh = open(self.get_file_name(), 'wt')
        css = Template(css_template)
        sizes_dict = {}
        for i in range(12):
            sizes_dict['w_unit%d' % i] = '%fin' % (i*self.get_cell_width())
            sizes_dict['h_unit%d' % i] = '%fin' % (i*self.get_cell_height())
        css = css.substitute(sizes_dict)
        css += '.table-width {width: %fin; max-width: %fin; min-width: %fin; } ' % (
            self.get_table_width(),
            self.get_table_width(),
            self.get_table_width())
        for i in range(1, 10):
            css += '.limit-%drow {overflow:hidden;max-height:%fin; height: %fin;} ' % (
                i, self.get_cell_height()*i, self.get_cell_height()*i)
        for i in range(1, 33):
            css += '.limit-%dcol {overflow: hidden;max-width: %fin;width: %fin;} ' % (
                i, self.get_cell_width()*i, self.get_cell_width()*i)
        contents = Template(main_template)
        contents = contents.substitute(title=self.get_title(),
                                       day=self.day_name,
                                       slice=self.time_range.name,
                                       theader=self.get_table_header(),
                                       detail=self.get_table_rows(),
                                       tfoot=self.get_table_foot(),
                                       bottom=self.get_page_bottom(),
                                       css=css,
                                       zambia_ver=self.version, 
                                       event=config.event_name
                                       )
        fh.write(contents)
        fh.close()

    # Convenience function: Show us the work when it's done. Only 
    # known to work on Macintosh.
    def open(self):
        os.system('open "%s"' % self.get_file_name())
