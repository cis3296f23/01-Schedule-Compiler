from numpy import arange, sin, pi
import matplotlib
import matplotlib.colors as mcolors
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import wx
from algo import Schedule
import pandas as pd

class CanvasPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.figure = Figure()
        
        self.axes = []
        for i in range(511,516):
            self.axes.append(self.figure.add_subplot(i))
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()

    def draw(self,schedules:list[Schedule]):
        # Predefined colors for consistency
        colors = list(mcolors.TABLEAU_COLORS.values())
        course_colors = {}

        def military_time_to_number(military_time):
            # Makes sure the time is in a 4-digit format
            military_time_str = f"{military_time:04d}"  
            hour = int(military_time_str[:2])
            minute = int(military_time_str[2:])
            return hour + minute / 60
        
        def decimal_time_to_standard(decimal_time):
            hours = int(decimal_time)
            minutes = int(round((decimal_time - hours) * 60 / 5) * 5)  # Round to nearest 5 because converting back resulting in error with exact
            if minutes == 60:  # Handle the case where rounding leads to 60 minutes
                hours += 1
                minutes = 0
            return f'{hours:02d}:{minutes:02d}'
    
        for i in range(0,5):
            self.axes[i].clear()
            self.axes[i].invert_yaxis()
            labels_added = set()
            # A dictionary to map days to numbers
            day_to_num = {'Sunday': 1, 'Monday': 2, 'Tuesday': 3, 'Wednesday': 4, 'Thursday': 5, 'Friday': 6, 'Saturday': 7}
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
            
            self.axes[i].plot()