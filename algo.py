from plotting import MainFrame
import wx

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

def dfs_build_rosters(course_info:dict, term:str, course_keys:list[str], index:int, roster:Schedule, valid_rosters:list[Schedule], unavail_times:Schedule):
    """
    Goes through the sections of the course in course_info indicated by index of course_keys via depth-first search for courses that fit the schedule as is and without overlapping with unavail_times
    @param course_info : information about the sections of each course
    @param term : semester to build roster for
    @param course_keys : list of course names in the format "subject course_number"
    @param index : index of course_keys to use
    @param roster : temporary Schedule variable to store potential roster to add and remove from
    @param valid_rosters : list of schedules that have sections for every course the user wants to take
    @param unavail_times : Schedule variable representing times the user is not available
    """
    # If 5 schedules have already been created, return
    if len(valid_rosters) >= 5:
        return
    #if no courses were inputted, return
    if term not in course_info or not course_info[term]:
        return
    # If all courses have been considered, add the current roster to valid_rosters
    if index == len(course_keys):
        valid_rosters.append(roster.copy())
        return

    course_key = course_keys[index]
    if course_key in course_info[term]:
        for section in course_info[term][course_key]:
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
            if not overlaps_with_unavail and roster.add_class(section['schedule'], section):  # Check for overlap with unavailable times
                dfs_build_rosters(course_info, term, course_keys, index + 1, roster, valid_rosters, unavail_times)
                roster.remove_class(section['schedule'], section)

def build_all_valid_rosters(course_info:dict, term:str, course_list:list[str], unavail_times:Schedule):
    """
    Calls the depth_first_search with valid_rosters as a parameter to update and then sorts the schedule by timeslot for each day and adds the section info
    @param course_info : dictionary of course mapped to the info for each section of it
    @param term : semester to build roster for
    @param course_list : list of str courses in "subject course_number" format
    @param unavail_times : schedule with times that the user is not available
    @return sorted_valid_rosters : a list of at most 5 potential schedules with sorted timeslots and section information
    """
    valid_rosters = []
    dfs_build_rosters(course_info, term, course_list, 0, Schedule(), valid_rosters, unavail_times)
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

def plot_schedule(schedules):
    """
    Creates the window for the wx app which displays the roster graphs and calls a function to draw and display each graph on each page
    """
    app = wx.App(False)
    MainFrame(schedules).Show()
    app.MainLoop()
    app.ExitMainLoop()