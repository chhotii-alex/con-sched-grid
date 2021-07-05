import os
from string import Template
import location

main_template = '''
<!DOCTYPE html>
<html>
<head>
<style>
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
.limit-1row {
overflow: hidden;
max-height: 25px;
}
.limit-2row {
overflow: hidden;
max-height: 50px;
}
.limit-3row {
overflow: hidden;
max-height: 75px;
}
.limit-4row {
overflow: hidden;
max-height: 100px;
}
.limit-1col {
 max-width: 25px;
}
.limit-2col {
 max-width: 50px;
}
.limit-3col {
 max-width: 75px;
}
.limit-4col {
 max-width: 100px;
}
.limit-5col {
 max-width: 125px;
}
.limit-6col {
 max-width: 150px;
}
.limit-7col {
 max-width: 175px;
}
.limit-8col {
 max-width: 200px;
}
.limit-9col {
 max-width: 225px;
}
.limit-10col {
 max-width: 250px;
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
 border: None;
 font-size: 11px;
 width: 100px;
 height: 25px;
}
.first-room {
 border-top: 1px solid black;
}
.time-head {
 color: white;
 font-size: 9px;
 background-color: black;
 width: 25px;
 max-width: 25px; 
}
.gray {
  background-color: #888888;
}
.schedule_item {
  font-family: 'Times New Roman', serif;
  font-size: 12px;
}
.event-name {
}
.center {
text-align: center;
font-weight: bold;
}

</style>
<title>
$title
</title>
</head>
<body>
<div class="event-name">Arisia 2022</div>
<div class="center">$day $slice</div>
<br/>
$detail
</body>
</html>
'''

class Placeholder:
    def __init__(self, time_minute_of_day, duration):
        self.time_minute_of_day = time_minute_of_day
        self.duration = duration

    def is_placeholder(self):
        return True

    def get_time_minute_of_day(self):
        return self.time_minute_of_day

    def get_duration(self):
        return self.duration

class BucketList:
    def __init__(self, time_range):
        self.time_range = time_range
        self.buckets = []
        for _ in range(time_range.interval_count()):
            self.buckets.append([]) 

    def insert(self, session):
        bucket_number = self.time_range.index_for_time(
            session.get_time_minute_of_day())
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

class GridPage:
    def __init__(self, day_name, time_range, sessions):
        self.day_name = day_name
        self.time_range = time_range
        self.sessions_per_room = {}
        for room in location.get_used_rooms():
            self.sessions_per_room[room] = BucketList(time_range)
        for session in sessions:
            first = True
            for room in session.get_rooms():
                if room.should_display():
                    if first:
                        self.sessions_per_room[room].insert(session)
                        first = False
                    else:
                        self.sessions_per_room[room].insert(
                            Placeholder(session.get_time_minute_of_day(),
                                        session.get_duration()))

    def get_file_name(self):
        return "%s%s.html" % (self.day_name[0:3], self.time_range.name[0:4])

    def get_title(self):
        return "Grid for %s %s" % (self.day_name, self.time_range.name)

    def get_detail_for_room(self, room, is_first):
        if is_first:
            class_string = 'first-room'
        else:
            class_string = ''
        results = '<td class="room-name %s"><div class="room-name">' % (class_string)
        results += str(room)
        results += '</div></td>'
        bucket_list = self.sessions_per_room[room]
        interval_max = self.time_range.interval_count()
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

    def get_table_rows(self):
        rows = '''
        <table>
        <tr>
        <td colspan="2" width="200px"></td>
        '''
        for time_str in self.time_range.time_strings():
            rows += '<td class="time-head"><div class="time-head">'
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
            rows += '<tr>'
            rows += '<td rowspan="%d" height="%dpx">' % (
                len(rooms), 25*len(rooms))
            rows += '<div class="level-name" width="20px">'
            rows += level.name
            rows += " (%s)" % level.short_name
            rows += '</div>'
            rows += '</td>'

            rows += self.get_detail_for_room(rooms[0], True)
            
            rows += '</tr>'
            for room in rooms[1:]:
                rows += '<tr>'
                rows += self.get_detail_for_room(room, False)
                rows += '</tr>'
        rows += '''
        </tbody>
        </table>
        '''
        return rows

    def write(self):
        fh = open(self.get_file_name(), 'wt')
        contents = Template(main_template)
        contents = contents.substitute(title=self.get_title(),
                                       day=self.day_name,
                                       slice=self.time_range.name,
                                       detail=self.get_table_rows())
        fh.write(contents)
        fh.close()

    # Convenience function: Show us the work when it's done. Only 
    # known to work on Macintosh.
    def open(self):
        os.system('open "%s"' % self.get_file_name())
