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
        generalFrame=ttk.Frame(self.__root)
        generalFrame.pack(fill=BOTH, expand=1, anchor=CENTER)
        #Scrollbar implementation
        canv = Canvas(generalFrame)
        canv.pack(side=LEFT,fill=BOTH,expand=1,anchor=CENTER)
        mainScrollBar = ttk.Scrollbar(generalFrame,orient=VERTICAL,command=canv.yview)
        mainScrollBar.pack(side='right',fill=Y)
        canv.configure(yscrollcommand=mainScrollBar.set)
        canv.bind('<Configure>', lambda e: canv.configure(scrollregion=canv.bbox("all")))
        secondFrame = Frame(canv)
        secondFrame.pack(fill=BOTH,expand=1)
        canv.create_window((0,0), window=secondFrame, anchor = "nw",height=800,width=3000)
        
        self.__style = ttk.Style()
        self.__style.configure('TButton', font = ('Courier',12,'bold'))
        self.__style.configure('Header.TLabel', font = ('Courier',18,'bold'))
        self.build_general_frame(secondFrame) #Second frame is basically the new root/generalFrame now
    
    def build_general_frame(self,master):
        """
        Builds the GUI
        @param master : root application
        """
        #degree program selection gui
        ttk.Label(master,text='Select a degree program (can type to narrow down, no worries if your program is not in the list):').grid(row=0,column=0)
        self.degr_prog_to_url = temple_requests.get_degr_progs()
        self.all_degr_progs = list(self.degr_prog_to_url.keys())
        self.all_degr_progs_var = Variable()
        self.all_degr_progs_var.set(self.all_degr_progs)
        self.degr_prog_entry = ttk.Entry(master,width=30)
        self.degr_prog_entry.grid(row=1,column=0)
        degr_prog_scrollbar = ttk.Scrollbar(master,orient=VERTICAL)
        degr_prog_scrollbar.grid(row = 1, column =1, sticky = N+S+W+E)
        self.degr_prog_listbox = Listbox(master,listvariable=self.all_degr_progs_var,selectmode='single',width=70,height=10)
        self.degr_prog_listbox.grid(row=2,column=0)
        self.degr_prog_listbox.configure(yscrollcommand=degr_prog_scrollbar.set)
        self.degr_prog_listbox.bind('<<ListboxSelect>>',self.pick_degr_prog)
        degr_prog_scrollbar.config(command=self.degr_prog_listbox.yview)
        self.degr_prog_entry.bind('<KeyRelease>', self.narrow_search) 
        #course entry gui
        self.curr_curric = None
        ttk.Label(master,text="Enter your course (Notes: 1. add by top priority to least priority if desired 2. can type to search 3. can add course even if not in list):").grid(row=3,column=0)
        self.course_entry=ttk.Entry(master,width=50)
        self.course_entry.grid(row=4,column=0)
        self.course_lstbox = Listbox(master,selectmode='single',width=30,height=10)
        self.course_lstbox.grid(row=5,column=0)
        self.course_retrieval_btn = ttk.Button(master,text='Add Course',command=self.get_courses)
        self.course_retrieval_btn.grid(row=6,column=0)
        #add course to list
        self.add_course_btn = ttk.Button(master, text="Add Course to List", command=self.add_course_to_list)
        self.add_course_btn.grid(row=7, column=0)
        self.added_courses_textbox = Text(master, width=30, height=10)
        self.added_courses_textbox.grid(row=8, column=0, columnspan=2) 
        #schedule info gui
        self.course_entry=ttk.Entry(master,width=20)
        self.course_entry.grid(row=9,column=0)
        self.schedule_info_btn = ttk.Button(master,text="Get schedule info",command=self.get_schedule_info)
        self.schedule_info_btn.grid(row=10,column=0)
        self.schedule__info_btn_output = Text(master,width=150,height=7)
        self.schedule__info_btn_output.grid(row=11,column=0)
        #professor name entry
        ttk.Label(master,text="Enter a professor name:").grid(row=10,column=0)
        self.prof_entry=ttk.Entry(master,width=30)
        self.prof_entry.grid(row=12,column=0)
        self.rmp_button = ttk.Button(master,text="Get RMP Rating",command=self.retrieve_rmp_data)
        self.rmp_button.grid(row=13,column=0)
        self.rmp_output = Text(master,width=80,height=5)
        self.rmp_output.grid(row=14,column=0)
        #enter number of credits
        ttk.Label(master, text="Enter the number of credits (min to max):").grid(row=15, column=0)
        self.low_entry = ttk.Entry(master, width=3)
        self.low_entry.grid(row=16, column=0, padx=2, pady=2)
        ttk.Label(master, text="to").grid(row=17, column=0, padx=2, pady=2)
        self.high_entry = ttk.Entry(master, width=3)
        self.high_entry.grid(row=18, column=0, padx=2, pady=2)
        self.submit_range_btn = ttk.Button(master, text="Submit Range", command=self.submit_range)
        self.submit_range_btn.grid(row=19, column=0)
        self.outputt= Text(master, width = 50, height=1)
        self.outputt.grid(row=20, column=0)

    def narrow_search(self,filler):
        """
        Narrows down degree programs based on the string the user is entering
        @param filler : placeholder for when the function is called as an event and an extra parameter is given
        """
        query = self.degr_prog_entry.get()
        if not query:
            self.update_degr_prog_listbox(self.all_degr_progs)
        else:
            data = []
            for degr_prog in self.all_degr_progs:
                if query.lower() in degr_prog.lower():
                    data.append(degr_prog)

    def update_degr_prog_listbox(self,data):
        """
        Updates the listbox with the degree programs in data
        """
        self.degr_prog_listbox.delete(0, 'end')
        for degr_prog in data: 
            self.degr_prog_listbox.insert('end', degr_prog)
        
    def pick_degr_prog(self,event):
        self.degr_prog_entry.delete(0,END)
        selec_ind = self.degr_prog_listbox.curselection()
        if selec_ind:
            degr_prog = self.degr_prog_listbox.get(selec_ind)
            self.degr_prog_entry.insert(0,degr_prog)
            curric = Variable()
            self.curr_curric = temple_requests.get_curric(self.degr_prog_to_url[degr_prog])
            curric.set(self.curr_curric)
            self.course_lstbox.config(listvariable=curric) 

    def get_courses(self):
        self.retrieval_btn_output.insert(END,temple_requests.get_curric(self.degree_prog_entry.get()))

    def get_schedule_info(self):
        course = self.course_entry.get()
        self.schedule__info_btn_output.insert(END,temple_requests.get_course_sections_info('202403',course[:course.find(' ')],course[course.find(' ')+1:],''))

    def retrieve_rmp_data(self):
        prof = self.prof_entry.get()
        rating_info = temple_requests.get_rmp_data(prof)
        self.rmp_output.insert(END,"Professor " + prof + " has a rating of " + str(rating_info[0]) + " from " + str(rating_info[1]) + " reviews.")

    def submit_range(self):
        low_value = self.low_entry.get()
        high_value = self.high_entry.get()
        self.outputt.insert(END, "From " + str(low_value) + " to " + str(high_value) + " credits.")   

    def add_course_to_list(self):
        selected_course = self.course_lstbox.get(ANCHOR)
        if selected_course:
            self.added_courses_textbox.insert(END, selected_course + '\n')
    
    def get_courses(self):
        courses = temple_requests.get_curric(self.degree_prog_entry.get())
        self.course_lstbox.delete(0, END)
        for course in courses:
            self.course_lstbox.insert(END, course)