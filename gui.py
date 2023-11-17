from tkinter import *
from tkinter import ttk
import temple_requests
import threading

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
        ttk.Label(master,text='Select a degree program:').grid(row=0,column=0)
        self.all_degr_progs = list(temple_requests.get_degr_progs().keys())
        self.all_degr_progs_var = Variable()
        self.all_degr_progs_var.set(self.all_degr_progs)
        self.degr_prog_entry = ttk.Entry(master,width=30)
        self.degr_prog_entry.grid(row=0,column=0)
        degr_prog_scrollbar = ttk.Scrollbar(master,orient=VERTICAL)
        degr_prog_scrollbar.grid(row = 1, column =1, sticky = N+S+W+E)
        self.degr_prog_listbox = Listbox(master,listvariable=self.all_degr_progs_var,selectmode='single',width=40,height=10)
        self.degr_prog_listbox.grid(row=1,column=0)
        self.degr_prog_listbox.configure(yscrollcommand=degr_prog_scrollbar.set)
        degr_prog_scrollbar.config(command=self.degr_prog_listbox.yview)
        self.degr_prog_entry.bind('<KeyRelease>', self.narrow_search_thread) 
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
        # Entering number of credits
        ttk.Label(master, text="Enter the number of credits (min to max):").grid(row=14, column=0)
        self.low_entry = ttk.Entry(master, width=3)
        self.low_entry.grid(row=15, column=0, padx=2, pady=2)
        ttk.Label(master, text="to").grid(row=16, column=0, padx=2, pady=2)
        self.high_entry = ttk.Entry(master, width=3)
        self.high_entry.grid(row=17, column=0, padx=2, pady=2)
        self.submit_range_btn = ttk.Button(master, text="Submit Range", command=self.submit_range)
        self.submit_range_btn.grid(row=18, column=0)
        self.outputt= Text(master, width = 50, height=1)
        self.outputt.grid(row=19, column=0)

    def narrow_search_thread(self,filler):
        """
        Enables the GUI to run as one thread and the autocomplete as another
        """
        #need to add synchronization
        threading.Thread(target=self.narrow_search).start()
    
    def narrow_search(self):
        """
        Narrows down degree programs based on the string the user is entering
        """
        query = self.degr_prog_entry.get()
        if not query:
            self.update_degr_prog_listbox(self.all_degr_progs)
        else:
            data = []
            for degr_prog in self.all_degr_progs:
                if query.lower() in degr_prog.lower():
                    data.append(degr_prog)
            self.update_degr_prog_listbox(data)

    def update_degr_prog_listbox(self,data):
        """
        Updates the listbox with the degree programs in data
        """
        self.degr_prog_listbox.delete(0, 'end')
        for degr_prog in data: 
            self.degr_prog_listbox.insert('end', degr_prog)
        
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
