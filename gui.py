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
        ttk.Label(master,text="Enter your degree program (i.e Computer Science BS):").grid(row=2,column=0)
        self.degree_prog_entry=ttk.Entry(master,width=50)
        self.degree_prog_entry.grid(row=3,column=0)
        self.course_retrieval_button = ttk.Button(master,text='Get Required Courses',command=self.get_courses)
        self.course_retrieval_button.grid(row=4,column=0)
        ttk.Label(master,text="Courses in the curriculum:").grid(row=5,column=0)
        self.retrieval_button_output = Text(master,width=150,height=15)
        self.retrieval_button_output.grid(row=6,column=0)
    
    def get_courses(self):
        self.retrieval_button_output.insert(END,temple_requests.get_curric(self.degree_prog_entry.get()))

if __name__=='__main__':
    root = Tk()
    app = GUI(root)
    root.mainloop()
    exit(0)