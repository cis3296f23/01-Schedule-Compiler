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

    def add_timeslot(self, day:str, start_time:int, end_time:int,meeting_type:str)->bool:
        """
        Adds the given timeslot of (start_time,end_time) if valid
        @param day : str day of the week
        @param start_time
        @param end_time
        @return True on success, False on failure (invalid parameters)
        """
        if self.days.get(day)==None:
            print(f"Invalid day: {day}")
            return False
        if start_time>end_time:
            print("Invalid Range: Start time must be before end time")
            return False

        time_slot = ((start_time, end_time),meeting_type)
        
        self.days[day].append(time_slot)
        return True
    
    def remove_timeslot(self, day:str, start_time:int, end_time:int):
        """
        Remove method for external modules to call
        @param day : day of the week in all lowercase for the timeslot
        @param start_time
        @param end_time
        """
        #test this
        time_to_remove = None
        for timeslot in self.days[day]:
            if timeslot[0]==(start_time,end_time):
                time_to_remove = timeslot
                break
        self.days[day].remove(time_to_remove)
        
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
                    if self.timeslots_overlap(existing_timeslot[0], new_timeslot[0]):
                        return False

        for day, new_timeslots in class_meeting_times.days.items():
            for new_timeslot, meeting_type in new_timeslots:
                self.days[day].append((new_timeslot,meeting_type))

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
            for timeslot, meeting_type in timeslots:
                new_schedule.add_timeslot(day, timeslot[0], timeslot[1],meeting_type)
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
