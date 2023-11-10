from tkinter import *
from tkinter import ttk
import temple_requests

class GUI():
    def __init__(self,root):
        self.running = True
        self.__root = root
        self.__root.title('Schedule Compiler')
        #Can pick out style later
        title_label = ttk.Label(self.__root, text = 'Schedule Compiler', font='Fixedsys 35 bold', justify=CENTER)
        title_label.pack(padx=5,pady=5)

        self.__style = ttk.Style()
        self.__style.configure('TButton', font = ('Courier',12,'bold'))
        self.__style.configure('Header.TLabel', font = ('Courier',18,'bold'))

        generalFrame=ttk.Frame(self.__root)
        generalFrame.pack(padx=5,pady=5)
        self.build_general_frame(generalFrame)
    
    def build_general_frame(self,master):
        """
        Builds the GUI
        @param master : root application
        """
        ttk.Label(master,text='Select a degree program:').grid(row=0,column=0)
        self.degree_prog_dropdown = ttk.Combobox(master,values=temple_requests.get_degree_programs())
        self.degree_prog_dropdown.grid(row=1,column=0)


if __name__=='__main__':
    root = Tk()
    app = GUI(root)
    root.mainloop()
    exit(0)