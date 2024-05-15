class Schedule:
    """
    Represents someone's schedule with timeslots for each day and an attribute for class sections
    """
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

    def add_timeslot(self, day:str, start_time:int, end_time:int)->bool:
        """
        Adds the given timeslot of (start_time,end_time) if valid
        @param day : str day of the week
        @param start_time
        @param end_time
        @return True on success, False on failure (invalid parameters)
        """
        if day not in self.days:
            print(f"Invalid day: {day}")
            return False
        if start_time>end_time:
            print("Invalid Range: Start time must be before end time")
            return False

        time_slot = (start_time, end_time)
        
        self.days[day].append(time_slot)
        return True
    
    def remove_timeslot(self, day:str, start_time:int, end_time:int):
        """
        Remove method for external modules to call
        @param day : day of the week in all lowercase for the timeslot
        @param start_time
        @param end_time
        """
        self.days[day].remove((start_time,end_time))
        
    def add_class(self, class_meeting_times, sect_info:dict):
        """
        Adds the class section's meeting times to the schedule and the section's info if there is no overlap in the current schedule
        @param class_meeting_times
        @param sect_info : dictionary of information about the section of the course
        @return : False on failure, True on success
        """
        for day, new_timeslots in class_meeting_times.days.items():
            for new_timeslot in new_timeslots:
                for existing_timeslot in self.days[day]:
                    if self.timeslots_overlap(existing_timeslot, new_timeslot):
                        return False

        for day, new_timeslots in class_meeting_times.days.items():
            for new_timeslot in new_timeslots:
                self.days[day].append(new_timeslot)

        self.sections.append(sect_info)  # Store the section info
        return True

    def remove_class(self, class_meeting_times, sect_info:dict):
        """
        Removes the class meeting times from the schedule and the corresponding section info
        @param class_meeting_times
        @param sect_info : dictionary of information about the section of the course
        """
        for day, timeslots in class_meeting_times.days.items():
            for timeslot in timeslots:
                self.days[day].remove(timeslot)
        
        self.sections.remove(sect_info)  # Remove the section info
                
    @staticmethod
    def timeslots_overlap(slot1:tuple[int], slot2:tuple[int])->bool:
        """
        Checks if timeslots overlap
        @param slot1 : tuple with two integers representing a timeslot
        @param slot2 : tuple with two integers representing a timeslot
        @return : True if timeslots overlap, otherwise False
        """
        start1, end1 = slot1
        start2, end2 = slot2
        return not (end1 <= start2 or end2 <= start1)
    
    def copy(self):
        """
        Creates a copy of the object
        """
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
        """
        String version of the object
        """
        return str(self.days)

    def __eq__(self, value: object) -> bool:
        """
        Overrides the default equals method to check if the Schedule object value has the same sections array
        @param value : object that the current Schedule object self is being compared to
        @return True if the sections of the Schedule objects are equal, False if value is not a Schedule object or if the sections are not equal
        """
        if type(value)!=type(self):
            return False
        return self.sections==value.sections
    
    def __bool__(self) -> bool:
        """
        Overrides the boolean method to check if the sections array is empty
        @return True if self.sections is not empty, False otherwise
        """
        return bool(self.sections)

def is_subset_of_roster_in_lst(roster:dict,lst:list[Schedule]):
    for sched in lst:
        subset_tracker = [section in sched.sections for section in roster]
        if all(subset_tracker):
            return True
    return False

def dfs_build_rosters(course_info:dict, term:str, course_keys:list[str], index:int, roster:Schedule, valid_rosters:list[Schedule], unavail_times:Schedule, credits:int, max_credits:int):
    """
    Goes through the sections of the course in course_info indicated by index of course_keys via depth-first search for courses that fit the schedule as is and without overlapping with unavail_times
    @param course_info : information about the sections of each course
    @param term : semester to build roster for
    @param course_keys : list of course names in the format "subject course_number"
    @param index : index of course_keys to use
    @param roster : temporary Schedule variable to store potential roster to add and remove from
    @param valid_rosters : list of schedules that have sections for every course the user wants to take
    @param unavail_times : Schedule variable representing times the user is not available
    @param credits : number of credits for the built roster so far
    @param max_credits : maximum desired amount of credits for schedules
    """
    # If 5 schedules have already been created, return
    if len(valid_rosters) >= 5:
        return
    course_sections = course_info[term].get(course_keys[index]) if index<len(course_keys) else None
    # If all courses have been considered or the last course is being considered but would pass the credit limit if added, add the current roster to valid_rosters
    if index == len(course_keys) or (index==len(course_keys)-1 and course_sections and credits+course_sections[0]["creditHours"]>max_credits):
        #also check if roster is subset (then don't add) or if any of the rosters there are a subset of roster (then replace)
        if roster and not is_subset_of_roster_in_lst(roster.sections,valid_rosters):
            valid_rosters.append(roster.copy())
        return
    if course_sections:
        for section in course_sections:
            course_added = False
            if section['seatsAvailable'] and credits+section['creditHours']<=max_credits:
                overlaps_with_unavail = False
                for day, new_timeslots in section['schedule'].days.items():
                    for new_timeslot in new_timeslots:
                        for unavail_slot in unavail_times.days[day]:
                            if Schedule.timeslots_overlap(unavail_slot, new_timeslot):
                                overlaps_with_unavail = True
                                break
                        if overlaps_with_unavail:
                            break
                    if overlaps_with_unavail:
                        break
                if not overlaps_with_unavail:
                    course_added = roster.add_class(section['schedule'], section)
            dfs_build_rosters(course_info, term, course_keys, index + 1, roster, valid_rosters, unavail_times,credits+section['creditHours'] if course_added else credits,max_credits)
            if course_added:
                roster.remove_class(section['schedule'], section)

def build_all_valid_rosters(course_info:dict, term:str, course_list:list[str], unavail_times:Schedule, max_credits:int):
    """
    Calls the depth_first_search with valid_rosters as a parameter to update and then sorts the schedule by timeslot for each day and adds the section info
    @param course_info : dictionary of course mapped to the info for each section of it
    @param term : semester to build roster for
    @param course_list : list of str courses in "subject course_number" format
    @param unavail_times : schedule with times that the user is not available
    @return sorted_valid_rosters : a list of at most 5 potential schedules with sorted timeslots and section information
    @param max_credits : maximum desired amount of credits for schedules
    """
    #if no courses were inputted, return
    if not course_info.get(term):
        return []
    valid_rosters = []
    dfs_build_rosters(course_info, term, course_list, 0, Schedule(), valid_rosters, unavail_times,0, max_credits)
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