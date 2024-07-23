from tkinter import *
from tkinter import ttk
class TextRedirector(object):
    """
    Sets up object that sys.stdout is assigned as so that printed errors are redirected to a tkinter widget's text field
    Credit to Bryan Oakley on https://stackoverflow.com/questions/12351786/how-to-redirect-print-statements-to-tkinter-text-widget
    """
    def __init__(self,widget:Text,tag='stdout'):
        self.widget=widget
        self.tag = tag

    def write(self,text):
        self.widget.configure(state='normal')
        self.widget.insert('end',text,(self.tag,))
    #created to avoid the exception that appears when there is no flush method
    def flush(self):
        pass