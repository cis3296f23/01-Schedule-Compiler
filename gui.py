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
        ttk.Label(master,text="Enter your CST degree program (i.e Computer Science BS):").grid(row=2,column=0)
        self.degree_prog_entry=ttk.Entry(master,width=50)
        self.degree_prog_entry.grid(row=3,column=0)
        #only works for cst degree programs (need to fix)
        self.course_retrieval_btn = ttk.Button(master,text='Get Required Courses',command=self.get_courses)
        self.course_retrieval_btn.grid(row=4,column=0)
        ttk.Label(master,text="Courses in the curriculum:").grid(row=5,column=0)
        self.retrieval_btn_output = Text(master,width=150,height=7)
        self.retrieval_btn_output.grid(row=6,column=0)
        self.course_entry=ttk.Entry(master,width=20)
        self.course_entry.grid(row=7,column=0)
        self.schedule_info_btn = ttk.Button(master,text="Get schedule info",command=self.get_schedule_info)
        self.schedule_info_btn.grid(row=8,column=0)
        self.schedule__info_btn_output = Text(master,width=150,height=7)
        self.schedule__info_btn_output.grid(row=9,column=0)
        ttk.Label(master,text="Enter a professor name:").grid(row=10,column=0)
        self.prof_entry=ttk.Entry(master,width=30)
        self.prof_entry.grid(row=11,column=0)
        self.rmp_button = ttk.Button(master,text="Get RMP Rating",command=self.retrieve_rmp_data)
        self.rmp_button.grid(row=12,column=0)
        self.rmp_output = Text(master,width=80,height=5)
        self.rmp_output.grid(row=13,column=0)


    def get_courses(self):
        self.retrieval_btn_output.insert(END,temple_requests.get_curric(self.degree_prog_entry.get()))

    def get_schedule_info(self):
        course = self.course_entry.get()
        self.schedule__info_btn_output.insert(END,temple_requests.get_course_sections_info('202403',course[:course.find(' ')],course[course.find(' ')+1:],''))

    def retrieve_rmp_data(self):
        prof = self.prof_entry.get()
        rating_info = temple_requests.get_rmp_data(prof)
        self.rmp_output.insert(END,"Professor " + prof + " has a rating of " + str(rating_info[0]) + " from " + str(rating_info[1]) + " reviews.")