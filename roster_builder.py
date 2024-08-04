from classes.Schedule import Schedule

def is_subset_of_roster_in_lst(sections:dict,lst:list[Schedule]):
    """
    Checks if the given roster is a subset of any of the rosters within the given list
    @param sections : dictionary of course section info
    @param lst : list of valid rosters
    @return True if roster is a subset of any of the rosters in list, False otherwise
    """
    for sched in lst:
        subset_tracker = [section in sched.sections for section in sections]
        if all(subset_tracker):
            return True
    return False

def remove_subset(schedule:Schedule,lst:list[Schedule]):
    """
    Removes a subset of sections within lst if it exists
    @param schedule : schedule to check if any schedule within the list is a subset of 
    @param lst : list of valid rosters
    """
    sched_to_replace = None
    for sched in lst:
        subset_tracker = [section in schedule.sections for section in sched.sections]
        if subset_tracker and all(subset_tracker):
            sched_to_replace=sched
            break
    if sched_to_replace:
        lst.remove(sched_to_replace)

def dfs_build_rosters(course_info:dict, term:str, campus_code:str, course_keys:list[str], index:int, roster:Schedule, valid_rosters:list[Schedule], unavail_times:Schedule, credits:int, max_credits:int, unavail_courses: set[str]):
    """
    Goes through the sections of the course in course_info indicated by index of course_keys via depth-first search for courses that fit the schedule as is and without overlapping with unavail_times
    @param course_info : information about the sections of each course
    @param term : semester to build roster for
    @param campus_code : str code for campus name
    @param course_keys : list of course names in the format "subject course_number"
    @param index : index of course_keys to use
    @param roster : temporary Schedule variable to store potential roster to add and remove from
    @param valid_rosters : list of schedules that have sections for every course the user wants to take
    @param unavail_times : Schedule variable representing times the user is not available
    @param credits : number of credits for the built roster so far
    @param max_credits : maximum desired amount of credits for schedules
    @param unavail_courses : courses with no seats available
    """
    # If 5 schedules have already been created, return
    if len(valid_rosters) >= 5:
        return
    course_sections = []
    if index<len(course_keys) and course_info[term][campus_code].get(course_keys[index]):
        course_sections = course_info[term][campus_code].get(course_keys[index])
    # If all courses have been considered or the last course is being considered but would pass the credit limit if added
    if index == len(course_keys) or (index==len(course_keys)-1 and course_sections and credits+course_sections[0]["creditHours"]>max_credits):
        #if roster is non-empty and is not a subset of a roster currently in the list
        if roster and not is_subset_of_roster_in_lst(roster.sections,valid_rosters):
            remove_subset(roster,valid_rosters)
            valid_rosters.append(roster.copy())
        return
    compat_sections = []
    unavail_sections = 0
    for section in course_sections:
        if section['seatsAvailable'] and credits+section['creditHours']<=max_credits:
            overlaps_with_unavail = False
            for day, new_timeslots in section['schedule'].days.items():
                for new_timeslot in new_timeslots:
                    for unavail_slot in unavail_times.days[day]:
                        if Schedule.timeslots_overlap(unavail_slot[0], new_timeslot[0]):
                            overlaps_with_unavail = True
                            break
                    if overlaps_with_unavail:
                        break
                if overlaps_with_unavail:
                    break
            if not overlaps_with_unavail:
                compat_sections.append(section)
        elif not section['seatsAvailable']:
            unavail_sections+=1
    if unavail_sections and unavail_sections==len(course_sections):
        unavail_courses.add(course_keys[index])
    for section in compat_sections:
        if roster.add_class(section['schedule'], section):
            dfs_build_rosters(course_info, term, campus_code, course_keys, index + 1, roster, valid_rosters, unavail_times,credits+section['creditHours'], max_credits, unavail_courses)
            roster.remove_class(section['schedule'], section)
    if len(compat_sections)!=len(course_sections) or not course_sections: #if at least one section was not able to be added, then try without the course
        dfs_build_rosters(course_info, term, campus_code, course_keys, index + 1, roster, valid_rosters, unavail_times, credits, max_credits, unavail_courses)


def build_all_valid_rosters(course_info:dict, term:str, campus_code:str, course_list:list[str], unavail_times:Schedule, max_credits:int):
    """
    Calls the depth_first_search with valid_rosters as a parameter to update and then sorts the schedule by timeslot for each day and adds the section info
    @param course_info : dictionary of course mapped to the info for each section of it
    @param term : semester to build roster for
    @param campus_code : str code for campus name
    @param course_list : list of str courses in "subject course_number" format
    @param unavail_times : schedule with times that the user is not available
    @return sorted_valid_rosters : a list of at most 5 potential schedules with sorted timeslots and section information
    @param max_credits : maximum desired amount of credits for schedules
    """
    #if no courses were inputted, return
    if not course_info.get(term):
        return []
    if not course_info[term].get(campus_code):
        return []
    valid_rosters = []
    unavail_courses = set()
    dfs_build_rosters(course_info, term, campus_code, course_list, 0, Schedule(), valid_rosters, unavail_times,0,max_credits,unavail_courses)
    if unavail_courses:
        for course in unavail_courses:
            print(f"{course} has no seats available in any of its sections.")
    # Sort the times in each schedule before returning
    sorted_valid_rosters = []
    for roster in valid_rosters:
        sorted_roster = Schedule()
        for day, timeslots in roster.days.items():
            sorted_timeslots = sorted(timeslots, key = lambda x : x[0])
            for timeslot, meeting_type in sorted_timeslots:
                sorted_roster.add_timeslot(day, timeslot[0], timeslot[1], meeting_type)
        sorted_roster.sections = roster.sections
        sorted_valid_rosters.append(sorted_roster)
    return sorted_valid_rosters
