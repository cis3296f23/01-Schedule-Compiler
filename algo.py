import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import Button

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
    if course_info[term]:
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
    # Function to convert military time to a number (930 to 9.5)
    def military_time_to_number(military_time):
        military_time_str = f"{military_time:04d}"  # Makes sure the time is in a 4-digit format
        hour = int(military_time_str[:2])
        minute = int(military_time_str[2:])
        return hour + minute / 60

    # Predefined colors for consistency
    colors = list(mcolors.TABLEAU_COLORS.values())
    course_colors = {}
    
    def draw_schedule(ax, schedule_data, schedule_number, my_schedule):
        ax.clear()
        ax.invert_yaxis()
        labels_added = set()
        # Decimal time to standard time
        def decimal_time_to_standard(decimal_time):
            hours = int(decimal_time)
            minutes = int(round((decimal_time - hours) * 60 / 5) * 5)  # Round to nearest 5 because converting back resulting in error with exact

            if minutes == 60:  # Handle the case where rounding leads to 60 minutes
                hours += 1
                minutes = 0

            return f'{hours:02d}:{minutes:02d}'

        for _, row in schedule_data.iterrows():
            color = course_colors[row['Course Name']]
            label = row['Course Name'] if row['Course Name'] not in labels_added else None
            labels_added.add(row['Course Name'])
            bar = ax.bar(row['Day'], row['End Time'] - row['Start Time'], bottom=row['Start Time'], 
                        color=color, edgecolor='black', label=label, align='center')

            # Adding time annotation to each bar in standard time format
            start_time = decimal_time_to_standard(row['Start Time'])
            end_time = decimal_time_to_standard(row['End Time'])
            ax.text(row['Day'], row['Start Time'] + (row['End Time'] - row['Start Time']) / 2, 
                    f'{start_time}-{end_time}', color='white', ha='center', va='center')
        
        # Setting labels and title
        ax.set_ylabel('Time (hours)')
        ax.set_title(f'Weekly Course Schedule: Chart {schedule_number}')
        ax.set_xticks(range(1, 6))
        ax.set_xticklabels(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])

        # Adjusting y-axis to show hours from 6 AM to 10 PM for ease of viewing
        ax.set_yticks(range(6, 23))
        ax.set_ylim(22, 6)

        # Handle legend
        ax.legend(title='Courses', bbox_to_anchor=(1.1, 1), loc='upper left')

    # Create a figure and axis with extra space for buttons and legend
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.subplots_adjust(bottom=0.15, right=0.8)

    # A dictionary to map days to numbers
    day_to_num = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5}

    # Prepare data for each schedule
    schedule_data_list = []
    for my_schedule in schedules:
        data = []
        for section in my_schedule.sections:
            course_name = section['name']
            if course_name not in course_colors:
                course_colors[course_name] = colors[len(course_colors) % len(colors)]
            for day, timeslots in section['schedule'].days.items():
                for timeslot in timeslots:
                    start_time, end_time = timeslot
                    data.append({'Course Name': course_name, 'Day': day_to_num[day.capitalize()], 
                                 'Start Time': military_time_to_number(start_time), 
                                 'End Time': military_time_to_number(end_time)})
        schedule_data_list.append(pd.DataFrame(data))

    current_schedule = [0]  # Using a list to modify the current index inside the functions

    # Navigation functions
    def next_schedule(event):
        if schedules:
            current_schedule[0] = (current_schedule[0] + 1) % len(schedules)
            draw_schedule(ax, schedule_data_list[current_schedule[0]], current_schedule[0] + 1, schedules[current_schedule[0]])
            plt.draw()

    def prev_schedule(event):
        if schedules:
            current_schedule[0] = (current_schedule[0] - 1) % len(schedules)
            draw_schedule(ax, schedule_data_list[current_schedule[0]], current_schedule[0] + 1, schedules[current_schedule[0]])
            plt.draw()

    # Adding buttons for navigation
    ax_prev_button = plt.axes([0.76, 0.025, 0.1, 0.04])
    ax_next_button = plt.axes([0.87, 0.025, 0.1, 0.04])
    btn_prev = Button(ax_prev_button, 'Previous')
    btn_next = Button(ax_next_button, 'Next')
    btn_prev.on_clicked(prev_schedule)
    btn_next.on_clicked(next_schedule)

    # Initial draw
    if current_schedule and current_schedule[0]<len(schedule_data_list):
        draw_schedule(ax, schedule_data_list[current_schedule[0]], current_schedule[0] + 1, schedules[current_schedule[0]])

    plt.show()

def display_course_info(schedules):
        # Create a figure for course information
        info_fig, info_ax = plt.subplots(figsize=(8, len(schedules) * 2))
        info_ax.axis('off')  # Turn off axis

        course_info_str = ''
        for i, my_schedule in enumerate(schedules):
            course_info_str += f'Chart {i + 1}\n'
            for section in my_schedule.sections:
                course_info = f"{section['name']} CRN: {section['CRN']} Professor: {section['professor']} Rating: {section['profRating']} # of Reviews: {section['numReviews']}\n"
                course_info_str += course_info
            course_info_str += '\n'

        # Displaying Course Info
        info_ax.text(0, 1, course_info_str, ha="left", va="top", fontsize=9, wrap=True)

        plt.show()