import os
from multiprocessing import Process, Pipe
from string import Template
import location
import contime

css_template = '''
body {
  font-family: Arial, sans-serif;
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
.center {
text-align: center;
font-weight: bold;
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
<div class="center">$day $slice</div>
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

class SessionSubinterval:
    def __init__(self, session, effective_duration):
        self.session = session
        self.effective_duration = effective_duration

    def is_placeholder(self):
        return self.session.is_placeholder()

    def get_duration(self):
        return self.effective_duration

    def get_room_count(self):
        return self.session.get_room_count()

    def get_title(self):
        return self.session.get_title() + \
            " <i>(" + self.session.get_time_str() + ")</i>"

class BucketList:
    def __init__(self, time_range):
        self.time_range = time_range
        self.buckets = []
        for _ in range(time_range.interval_count()):
            self.buckets.append([]) 

    def insert(self, session):
        bucket_number = self.time_range.index_for_time(
            session.get_time_minute_of_day())
        # Session may have started before start of time range... on 
        # previous day!
        # TODO: this is brittle if we introduce non-equal time ranges
        while bucket_number >= self.time_range.interval_count():
            bucket_number -= self.time_range.interval_count()*contime.time_ranges_per_day
        # Session may have started before start of time range.
        if bucket_number < 0:
            effective_duration = session.get_duration() + \
                bucket_number*self.time_range.minutes_per_box
            session = SessionSubinterval(session, effective_duration)
            bucket_number = 0
        self.buckets[bucket_number].append(session)

    def get_schedule(self):
        schedule = []
        empty_count = 0
        for bucket in self.buckets:
            if len(bucket):
                if empty_count > 0:
                    schedule.append( (empty_count, []) )
                intervals = self.time_range.intervals_for_duration(
                    bucket[0].get_duration())
                schedule.append( (intervals, bucket) )
                empty_count = 1 - intervals
            else:
                empty_count += 1
        if empty_count > 0:
            schedule.append( (empty_count, []) )
        return schedule

def get_detail_for_section(bucket_list, interval_max):
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

def multiprocess_details_for_section(connection):
    data = connection.recv()
    results = get_detail_for_section(data[0], data[1])
    connection.send(results)
    connection.close()

class GridPage:
    def __init__(self, day_name, time_range, sessions):
        self.connection_dictionary = None
        self.cell_height = 21
        self.cell_width = 26
        self.day_name = day_name
        self.time_range = time_range
        self.sessions_per_section = {}
        for section in location.get_used_sections():
            self.sessions_per_section[section] = BucketList(time_range)
        for session in sessions:
            first = True
            for section in session.get_sections():
                if section in self.sessions_per_section:
                    if first:
                        self.sessions_per_section[section].insert(session)
                        first = False
                    else:
                        self.sessions_per_section[section].insert(
                            Placeholder(session))

    def get_file_name(self):
        return "%s%s.html" % (self.day_name[0:3], self.time_range.name[0:4])

    def get_title(self):
        return "Grid for %s %s" % (self.day_name, self.time_range.name)

    def prime_detail_for_section(self, section):
        if self.connection_dictionary is None:
            self.connection_dictionary = {}
        if section in self.connection_dictionary:
            return
        bucket_list = self.sessions_per_section[section]
        interval_max = self.time_range.interval_count()
        parent_connection, child_connection = Pipe()
        p = Process(target=multiprocess_details_for_section, 
                    args=(child_connection,))
        p.start()
        parent_connection.send([bucket_list, interval_max])
        self.connection_dictionary[section] = (parent_connection, child_connection)

    def get_detail_for_section(self, section):
        self.prime_detail_for_section(section)
        (parent_connection, child_connection) = self.connection_dictionary[section]
        results = parent_connection.recv()
        self.connection_dictionary.pop(section, None)
        return results

    def get_table_rows(self):
        rows = '''
        <table>
        '''
        rows += '''<tr>
        <td colspan="2" width="200px" class="just-black"></td>
        '''
        for _ in range(self.time_range.interval_count()):
            rows += '<td col-span="1" class="limit-1col just-black"> </td>'
        rows += '</tr>'
        rows += '''
        <tr>
        <td colspan="2" width="200px"></td>
        '''
        for time_str in self.time_range.time_strings():
            rows += '<td class="time-head limit-1col" col-span="1">'
            rows += '<div class="time-head">'
            rows += time_str
            rows += '</div></td>'
        rows += '''
        </tr>
        <tbody>
        '''
        for level in location.gLevelList:
            rooms = level.get_used_rooms()
            if not rooms:
                continue
            first_room = True
            for room in rooms:
                sections = room.get_sections()
                for i in range(len(sections)):
                    if i == 0:
                        self.prime_detail_for_section(sections[0])
                    if i < len(sections)-1:
                        self.prime_detail_for_section(sections[i+1])
                    section = sections[i]
                    rows += '<tr>'
                    if first_room:
                        rows += '<td rowspan="%d" class="limit-%drow">' % (
                            len(level.get_used_sections()), len(rooms))
                        rows += '<div class="level-name" width="20px">'
                        rows += level.name
                        rows += " (%s)" % level.short_name
                        rows += '</div>'
                        rows += '</td>'
                    if i == 0:
                        if first_room:
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
                first_room = False
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
                                       css=css)
        fh.write(contents)
        fh.close()

    # Convenience function: Show us the work when it's done. Only 
    # known to work on Macintosh.
    def open(self):
        os.system('open "%s"' % self.get_file_name())
