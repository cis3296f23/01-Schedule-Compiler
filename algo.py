class Schedule:
    def __init__(self):
        self.days = {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday':[],
            'sunday':[]
        }

    def add_timeslot(self, day, start_time, end_time):
        if day not in self.days:
            print(f"Invalid day: {day}")
            return
        
        time_slot = (start_time, end_time)
        
        self.days[day].append(time_slot)
        
    def __str__(self):
        return str(self.days)

def add_class(roster, class_meetingTimes):
    for day, new_timeslots in class_meetingTimes.days.items():
        for new_timeslot in new_timeslots:
            for existing_timeslot in roster.days[day]:
                if timeslots_overlap(existing_timeslot, new_timeslot):
                    return False
            
    for day, new_timeslots in class_meetingTimes.days.items():
        for new_timeslot in new_timeslots:
            roster.days[day].append(new_timeslot)
        
    return True

def remove_class(roster, class_meetingTimes):
    for day, timeslots in class_meetingTimes.days.items():
        for timeslot in timeslots:
            roster.days[day].remove(timeslot)

def timeslots_overlap(slot1, slot2):
    start1, end1 = slot1
    start2, end2 = slot2
    return not (end1 <= start2 or end2 <= start1)

def dfs_build_roster(course_info, course_keys, index, roster):
    # If all courses have been considered end the search
    if index == len(course_keys):
        return True

    course_key = course_keys[index]
    for section in course_info[course_key]:
        if add_class(roster, section['schedule']):
            if dfs_build_roster(course_info, course_keys, index + 1, roster):
                return True
            else:
                remove_class(roster, section['schedule'])

    return False

def build_complete_roster(course_info, course_list, roster:Schedule()):
    if dfs_build_roster(course_info, course_list, 0, roster):
        return roster
    return None