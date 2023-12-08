from numpy import arange, sin, pi
import matplotlib
import matplotlib.colors as mcolors
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import wx
import pandas as pd

class MainFrame(wx.Frame):
    def __init__(self,schedules):
        wx.Frame.__init__(self,None, title="Potential Rosters")
        main_panel = wx.Panel(self)
        nb = wx.Notebook(main_panel)
        panels = [] 
        for s in range(len(schedules)):
            panels.append(CanvasPanel(nb))
            nb.AddPage(panels[s],"Roster " + str(s+1))
            panels[s].draw(schedules,s)
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        main_panel.SetSizer(sizer)

#didn't add the different pages yet
class CanvasPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.figure = Figure()
        self.axes = self.figure.add_subplot(121)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()

    def draw(self,schedules:list, i:int):
        # Predefined colors for consistency
        colors = list(mcolors.TABLEAU_COLORS.values())
        course_colors = {}

        def military_time_to_number(military_time):
            # Makes sure the time is in a 4-digit format
            military_time_str = f"{military_time:04d}"  
            hour = int(military_time_str[:2])
            minute = int(military_time_str[2:])
            return hour + minute / 60

        def draw_schedule(ax, schedule_data, schedule_number):
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
            ax.set_xticks(range(1, 8))
            ax.set_xticklabels(['Sunday','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday'])

            # Adjusting y-axis to show hours from 6 AM to 10 PM for ease of viewing
            ax.set_yticks(range(6, 23))
            ax.set_ylim(22, 6)

            # Handle legend
            ax.legend(title='Courses', bbox_to_anchor=(1.1, 1), loc='upper left')
    
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
        # Initial draw
        if i<len(schedule_data_list):
            draw_schedule(self.axes, schedule_data_list[i], i+1)
        self.axes.plot()