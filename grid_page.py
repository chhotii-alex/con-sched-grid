import os
import math
from string import Template
import autosort
import location
import bucket
import contime

css_template = '''
body {
  font-family: Arial, sans-serif;
}
.page-third {
  width: ${third}px;
  display: inline-block;
}
table {
 table-layout: fixed;
 border: 1px solid black;
 border-collapse: collapse;
}
td {
border: 1px solid black;
overflow: hidden;
}
.level-name {
 border: 0.5px solid Gray;
 text-align: center;
 white-space: nowrap;
 vertical-align: middle;
 width: ${w_unit4};
}
.level-name div {
 transform: rotate(-90deg);
 font-size: 10px;
 margin-left: -6em;
 margin-right: -6em;
}
.room-name {
 border: 0.5px solid Gray;
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
<div class="table-width" >
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
$theader
$detail
$tfoot
$bottom
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
            yield bucket.Bucket(autosort.AutoSortedArray())

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
            results += '; '.join([s.get_title() for s in sessions])
            results += '''</div></td>
            '''
            curr_interval += interval
        return results

class GridPage:
    def __init__(self, day_name, time_range, sessions, page_number):
        self.cell_height = 21
        self.cell_width = 26
        self.day_name = day_name
        self.time_range = time_range
        self.sessions_per_section = {}
        self.page_number = page_number
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

    def get_detail_for_section(self, section):
        bucket_list = self.sessions_per_section[section]
        interval_max = self.time_range.interval_count()
        r = RowDetailMaker(bucket_list, interval_max)
        return r.get_cells_for_section()

    def get_table_width(self):
        return (6+self.time_range.interval_count())*self.cell_width

    def get_table_header(self):
        rows = '''
        <table class="table-width">
        '''
        rows += '''<tr>
        <td colspan="1" class="no-border limit-1col"></td>
        <td colspan="1" class="no-border limit-5col"></td>
        '''
        for _ in range(self.time_range.interval_count()):
            rows += '''<td colspan="1" class="limit-1col just-black"> </td>
                 '''
        rows += '</tr>'
        rows += '''
        <tr>
        <td colspan="1" class="no-border limit-1col"></td>
        <td colspan="1" class="no-border limit-5col"></td>
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
        return rows

    def get_row_start(self, level, room, section, is_1st_room, 
                      is_1st_section):
        results = '<tr>'
        if is_1st_room and is_1st_section:
            results += '<td rowspan="%d" class="level-name">' % (
                len(level.get_used_sections()) )
            results += '<div>'
            results += level.name
            results += " (%s)" % level.get_short_name()
            results += '</div>'
            results += '''</td>
             '''
        if is_1st_section:
            if is_1st_room:
                class_string = 'first_room'
            else:
                class_string = ''
            results += '<td class="room-name %s limit-5col" rowspan="%d">' % (
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
            sizes_dict['w_unit%d' % i] = '%dpx' % (i*self.cell_width)
            sizes_dict['h_unit%d' % i] = '%dpx' % (i*self.cell_height)
        sizes_dict['third'] = math.floor(self.get_table_width()/3) - 3
        css = css.substitute(sizes_dict)
        css += '.table-width {width: %dpx; max-width: %dpx; min-width: %dpx; display:block;} ' % (
            self.get_table_width(),
            self.get_table_width(),
            self.get_table_width())
        for i in range(1, 10):
            css += '.limit-%drow {overflow:hidden;max-height:%dpx; height: %dpx;} ' % (
                i, self.cell_height*i, self.cell_height*i)
        for i in range(1, 33):
            css += '.limit-%dcol {overflow: hidden;max-width: %dpx;width: %dpx;} ' % (
                i, self.cell_width*i, self.cell_width*i)
        contents = Template(main_template)
        contents = contents.substitute(title=self.get_title(),
                                       day=self.day_name,
                                       slice=self.time_range.name,
                                       theader=self.get_table_header(),
                                       detail=self.get_table_rows(),
                                       tfoot=self.get_table_foot(),
                                       bottom=self.get_page_bottom(),
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
