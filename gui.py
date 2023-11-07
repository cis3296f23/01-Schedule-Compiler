from tkinter import *
from tkinter import ttk

class GUI():
    def __init__(self,root):
        self.running = True
        self.__root = root
        self.__root.title('Schedule Compiler')
        #Can pick out style later
        title_label = ttk.Label(self.__root, text = 'Schedule Compiler', font='Daytona 35 bold', justify=CENTER)
        title_label.pack(padx=5,pady=5)

if __name__=='__main__':
    root = Tk()
    app = GUI(root)
    root.mainloop()
    exit(0)