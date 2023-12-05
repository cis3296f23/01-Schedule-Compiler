class Schedule:
    def __init__(self):
        self.days = {
            'sunday':[],
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday':[]
        }
        
        self.sections = []

    def add_timeslot(self, day, start_time, end_time):
        if day not in self.days:
            print(f"Invalid day: {day}")
            return
        
        time_slot = (start_time, end_time)
        
        self.days[day].append(time_slot)
    
    def remove_timeslot(self, day:str, start_time:int, end_time:int):
        """
        Remove method for external modules to call
        @param day : day of the week in all lowercase for the timeslot
        @param start_time
        @param end_time
        """
        self.days[day].remove((start_time,end_time))
        
    def add_class(self, class_meetingTimes, sect_info):
        for day, new_timeslots in class_meetingTimes.days.items():
            for new_timeslot in new_timeslots:
                for existing_timeslot in self.days[day]:
                    if self.timeslots_overlap(existing_timeslot, new_timeslot):
                        return False

        for day, new_timeslots in class_meetingTimes.days.items():
            for new_timeslot in new_timeslots:
                self.days[day].append(new_timeslot)

        self.sections.append(sect_info)  # Store the section info
        return True

    def remove_class(self, class_meetingTimes, sect_info):
        for day, timeslots in class_meetingTimes.days.items():
            for timeslot in timeslots:
                self.days[day].remove(timeslot)
        
        self.sections.remove(sect_info)  # Remove the section info
                
    @staticmethod
    def timeslots_overlap(slot1, slot2):
        start1, end1 = slot1
        start2, end2 = slot2
        return not (end1 <= start2 or end2 <= start1)
    
    def copy(self):
        new_schedule = Schedule()
        
        # Copying over the timeslots
        for day, timeslots in self.days.items():
            for timeslot in timeslots:
                new_schedule.add_timeslot(day, timeslot[0], timeslot[1])
        
        # Copying over the sections
        for section in self.sections:
            new_schedule.sections.append(section)
            
        return new_schedule
        
    def __str__(self):
        return str(self.days)

def dfs_build_rosters(course_info, course_keys, index, roster, valid_rosters):
    # If 5 schedules have already been created, return
    if len(valid_rosters) >= 5:
        return
    # If all courses have been considered, add the current roster to valid_rosters
    if index == len(course_keys):
        valid_rosters.append(roster.copy())
        return

    course_key = course_keys[index]
    if course_key in course_info:
        for section in course_info[course_key]:
            if roster.add_class(section['schedule'], section):  # Pass sect_info
                dfs_build_rosters(course_info, course_keys, index + 1, roster, valid_rosters)
                roster.remove_class(section['schedule'], section)  # Pass sect_info

def build_all_valid_rosters(course_info, course_list):
    valid_rosters = []
    dfs_build_rosters(course_info, course_list, 0, Schedule(), valid_rosters)
    # Sort the times in each schedule before returning
    sorted_valid_rosters = []

    for roster in valid_rosters:
        sorted_roster = Schedule()
        for day, timeslots in roster.days.items():
            sorted_timeslots = sorted(timeslots)
            for timeslot in sorted_timeslots:
                sorted_roster.add_timeslot(day, timeslot[0], timeslot[1])
        sorted_roster.sections = roster.sections
        sorted_valid_rosters.append(sorted_roster)

    return sorted_valid_rosters