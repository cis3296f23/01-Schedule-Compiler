from numpy import arange, sin, pi
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import wx
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

    def draw(self):
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
            self.axes[i].plot()