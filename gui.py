from tkinter import *
from tkinter import ttk
import temple_requests
import algo
from algo import Schedule
from text_redirection import TextRedirector
import sys,threading

class GUI():
    def __init__(self,root:Tk):
        """
        Initializes the title, screen, and frames used
        """
        self.running = True
        self.__root = root
        self.__root.title('Schedule Compiler')
        root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(),root.winfo_screenheight()))
        #Can pick out style later
        title_label = ttk.Label(self.__root, text = 'Schedule Compiler', font='Fixedsys 35 bold', justify=CENTER)
        title_label.pack(padx=5,pady=5)
        main_frame=ttk.Frame(self.__root)
        main_frame.pack(fill=BOTH, expand=1, anchor=CENTER)
        #Scrollbar implementation
        canv = Canvas(main_frame)
        canv.pack(side=LEFT,fill=BOTH,expand=1,anchor=CENTER)
        #creating a scroll bar and binding it to the entrire screen that the user uses
        main_scroll_bar = ttk.Scrollbar(main_frame,orient=VERTICAL,command=canv.yview)
        main_scroll_bar.pack(side='right',fill=Y)
        canv.configure(yscrollcommand=main_scroll_bar.set,)
        canv.bind('<Configure>', lambda e: canv.configure(scrollregion=canv.bbox("all")))
        #separate frame for all the widgets
        second_frame = Frame(canv)
        second_frame.pack(fill=BOTH,expand=1)
        canv.create_window((int(main_frame.winfo_screenwidth()/4),0), window=second_frame, anchor = "nw")
        self.added_courses = []
        self.course_info = dict()
        self.unavail_times = Schedule()
        self.__style = ttk.Style()
        self.__style.configure('TButton', font = ('Courier',12,'bold'))
        self.__style.configure('Header.TLabel', font = ('Courier',18,'bold'))
        self.build_general_frame(second_frame)
    
    def build_general_frame(self,master):
        """
        Builds the GUI
        @param master : root application
        """
        #degree program selection gui
        ttk.Label(master,text='Select a degree program if you would like to see a list of courses in the curriculum (can type to narrow down, no worries if your program is not in the list):').grid(row=0,column=0)
        self.degr_prog_to_url = temple_requests.get_degr_progs()
        self.all_degr_progs = list(self.degr_prog_to_url.keys())
        self.all_degr_progs_var = Variable()
        self.all_degr_progs_var.set(self.all_degr_progs)
        self.degr_prog_entry = ttk.Entry(master,width=30)
        self.degr_prog_entry.grid(row=1,column=0)
        self.degr_prog_listbox = Listbox(master,listvariable=self.all_degr_progs_var,selectmode='single',width=70,height=10)
        self.degr_prog_listbox.grid(row=2,column=0)
        self.degr_prog_listbox.bind('<<ListboxSelect>>',self.pick_degr_prog)
        self.degr_prog_entry.bind('<KeyRelease>', lambda filler : self.narrow_search(filler,entry=self.degr_prog_entry, lst=self.all_degr_progs, lstbox=self.degr_prog_listbox)) 
        #course entry gui
        self.curr_curric = []
        ttk.Label(master,text="Enter your course and press Enter key or button below to add (Notes: 1. add by top priority to least priority if desired 2. can type to search 3. can add course even if not in list):").grid(row=3,column=0)
        self.course_entry=ttk.Entry(master,width=50)
        self.course_entry.grid(row=4,column=0)
        self.curr_curric_var = Variable()
        self.curr_curric_var.set(self.curr_curric)
        self.course_lstbox = Listbox(master,selectmode='single',listvariable=self.curr_curric_var,width=15,height=10)
        self.course_lstbox.grid(row=5,column=0)
        self.course_lstbox.bind('<<ListboxSelect>>',lambda filler : self.insert_selection(filler, entry=self.course_entry,lstbox=self.course_lstbox))
        self.course_entry.bind('<KeyRelease>',lambda filler : self.narrow_search(filler, entry=self.course_entry, lst=self.curr_curric,lstbox=self.course_lstbox))
        self.course_entry.bind('<Return>',self.add_course_to_list)
        #buttons to add and remove courses
        self.add_course_btn = ttk.Button(master, text="Add Course to List", command= lambda  : self.add_course_to_list(event=None))
        self.add_course_btn.grid(row=6,column=0)
        self.remove_course_btn = ttk.Button(master, text="Remove Course from list", command=self.remove_course_from_list)
        self.remove_course_btn.grid(row=7,column=0)
        #listbox for displaying added courses
        self.added_courses_listbox = Listbox(master, width=15, height=7)
        self.added_courses_listbox.grid(row=8,column=0)
        #semester selection
        ttk.Label(master, text="Select the semester to create a schedule for:").grid(row=9, column=0)
        self.term_to_code = temple_requests.get_param_data_codes('getTerms')
        self.terms = list(self.term_to_code.keys())
        self.term_combobox = ttk.Combobox(master, values=self.terms, state="readonly")
        self.term_combobox.set(self.terms[1])
        self.term_combobox.grid(row=10, column=0)
        self.term_combobox.bind('<<ComboboxSelected>>', self.on_term_or_campus_selected)
        #select a campus
        ttk.Label(master, text="Select a Campus:").grid(row=11, column=0)
        self.campus_to_code = temple_requests.get_param_data_codes('get_campus')
        self.campuses = list(self.campus_to_code.keys())
        self.campus_combobox = ttk.Combobox(master, values=self.campuses, state="readonly")
        self.campus_combobox.set('Main')
        self.campus_combobox.grid(row=12, column=0)
        self.campus_combobox.bind('<<ComboboxSelected>>', self.on_term_or_campus_selected)
        #Credit entry
        ttk.Label(master, text="Enter the maximum number of credits you would like to take:").grid(row=13,column=0)
        self.high_entry = ttk.Entry(master, width=3)
        self.high_entry.grid(row=14,column=0)
        self.output= Text(master, width = 50, height=10)
        #day and time input
        ttk.Label(master, text="Add days and times you are NOT available (leave blank if available only Monday-Friday and not available during the weekend):").grid(row=15, column=0)
        # Days of the week selection
        ttk.Label(master, text="Select Day:").grid(row=16, column=0)
        self.days_dropdown = ttk.Combobox(master, values=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'] , state='readonly', width=20)
        self.days_dropdown.set('Sunday')
        self.days_dropdown.grid(row=17, column=0)
        # Times selection
        ttk.Label(master, text="Select Time Range:").grid(row=18, column=0)
        # Hour selection
        hours = [str(i) for i in range(0, 24)]
        self.start_hour_dropdown = ttk.Combobox(master, values=hours, state="readonly", width=3)
        self.start_hour_dropdown.grid(row=19, column=0)
        self.end_hour_dropdown = ttk.Combobox(master, values=hours, state="readonly", width=3)
        self.end_hour_dropdown.grid(row=20, column=0)
        # Minute selection
        minutes = [str(i) for i in range(0, 60, 5)]
        self.start_minute_dropdown = ttk.Combobox(master, values=minutes, state="readonly", width=3)
        self.start_minute_dropdown.grid(row=19, column=1, sticky=W)
        self.end_minute_dropdown = ttk.Combobox(master, values=minutes, state="readonly", width=3)
        self.end_minute_dropdown.grid(row=20, column=1, sticky=W)
        # Add button to add selected time
        self.add_time_btn = ttk.Button(master, text="Add Time", command=self.add_selected_time,width=15)
        self.add_time_btn.grid(row=21, column=0)
        #rmp checkbox
        ttk.Label(master, text="Check to prioritize courses by ratemyprofessors ratings:").grid(row=24)
        self.priorit_by_rmp_rating = BooleanVar()
        self.rmp_checkbox = Checkbutton(master,variable=self.priorit_by_rmp_rating)
        self.rmp_checkbox.grid(row=25)
        #compilation of schedules
        self.compile_button = ttk.Button(master,width=28,text="Compile Possible Schedules",command=self.compile_schedules)
        self.compile_button.grid(row=26)
        self.output.grid(row=27,column=0)
        sys.stdout = TextRedirector(self.output,'stdout')

    def on_term_or_campus_selected(self, event):
         self.__root.focus_set()

    def narrow_search(self,event:Event,entry:Entry,lst:list[str],lstbox:Listbox):
        """
        Narrows down degree programs based on the string the user is entering
        @param event : implicit parameter entered when a function is called as part of an event bind
        @param entry : entry to extract a string from (what the user has typed) to help narrow the search
        @param lst : master list to narrow down choices from
        @param lstbox : listbox/dropdown to update with narrowed down options
        """
        query = entry.get()
        if not query:
            #if the entry box has been cleared, updates the listbox with lst
            self.update_lstbox_options(event,lst,lstbox)
        else:
            data = []
            for item in lst:
                if query.lower() in item.lower():
                    data.append(item)
            self.update_lstbox_options(event,data,lstbox)

    def update_lstbox_options(self,event:Event,data:list[str],lstbox:Listbox):
        """
        Updates the listbox with the degree programs in data
        @param event : implicit parameter entered when a function is called as part of an event bind
        @param data : list with items to update the listbox with
        @param lstbox : listbox to update
        """
        lstbox.delete(0, 'end')
        for item in data: 
            lstbox.insert('end', item)
        
    def insert_selection(self,event: Event,entry:Entry,lstbox:Listbox):
        """
        Updates an entry box with the selected item in the listbox
        @param event : implicit parameter entered when a function is called as part of an event bind
        @param entry : entry to update
        @param lstbox : listbox from which to use value to update entry
        @return : index of selected item and the selected item if an item has been selected, otherwise None and None
        """
        entry.delete(0,END)
        selec_ind = lstbox.curselection()
        #if an item has been selected,
        if selec_ind:
            selection = lstbox.get(selec_ind)
            entry.insert(0,selection)
            return selec_ind, selection
        return None,None

    def pick_degr_prog(self,event:Event):
        """
        Updates degree program entry box with selected degree program and updates course listbox with the curriculum of the selected degree program
        @param event : implicit parameter entered when a function is called as part of an event bind
        """
        #updates degree program entry box
        selec_ind, selection = self.insert_selection(None,self.degr_prog_entry,self.degr_prog_listbox)
        #updates course selection listbox if a degree program was selected
        if selec_ind:
            curric = Variable()
            self.curr_curric = temple_requests.get_curric(self.degr_prog_to_url[selection])
            num_courses = len(self.curr_curric)
            for c in range(num_courses):
                self.curr_curric[c]=self.curr_curric[c].replace('\xa0',' ')
            curric.set(self.curr_curric)
            self.course_lstbox.config(listvariable=curric) 

    def add_course_to_list(self,event:Event):
        """
        Adds course entered in course entry to the added courses listbox
        """
        selected_course = self.course_entry.get()
        if selected_course and selected_course not in self.added_courses_listbox.get(0, END):
            self.added_courses_listbox.insert(END, selected_course)
            self.added_courses.append(selected_course)

    def remove_course_from_list(self):
        """
        Removes selected course in the added courses listbox from that listbox
        """
        selected_index = self.added_courses_listbox.curselection()
        if selected_index:
            self.added_courses_listbox.delete(selected_index)
            self.added_courses.pop(selected_index[0])

    def add_selected_time(self):
            selected_day = self.days_dropdown.get()
            start_hour = self.start_hour_dropdown.get()
            start_minute = self.start_minute_dropdown.get()
            end_hour = self.end_hour_dropdown.get()
            end_minute = self.end_minute_dropdown.get()
            if selected_day and start_hour and start_minute:
                self.unavail_times.add_timeslot(selected_day[0].lower()+selected_day[1:],int(str(start_hour)+str(start_minute)),int(str(end_hour)+str(end_minute)))
            else:
                print("Please select all components of the time.")
    
    def compile_schedules(self):
        print("Start schedule compilation process...")

        for course in self.added_courses:
            #semester hard coded, waiting on semester selection feature
            subj, course_num, attr = '', '', ''
            #can use regex later on to check if valid course was entered
            if course[-1].isnumeric():
                i = 0
                strlen_course = len(course)
                while i<strlen_course and course[i]!=' ':
                    subj+=course[i]
                    i+=1
                if i<strlen_course and course[i]==' ':
                    course_num+=course[i+1:]
            else:
                attr = course
                print(f"Processing course: {subj} {course_num} {attr}")
            #will instantiate prof_rating_cache when prof rating prioritization gui option is available
            temple_requests.get_course_sections_info(self.course_info,self.term_to_code[self.term_combobox.get()],subj,course_num,attr,self.campus_to_code[self.campus_combobox.get()],{},self.priorit_by_rmp_rating.get())
            
        valid_rosters = algo.build_all_valid_rosters(self.course_info,self.added_courses)
        print("Schedule compilation complete. Building the rosters...")
        for i, roster in enumerate(valid_rosters):
            print(f"Valid Roster {i + 1}:")
            print(roster)  # Print the schedule
            print("Sections in this Schedule:")
            for j, section in enumerate(roster.sections):
                print(str(j+1) + ". " + self.added_courses[i] + " CRN: " + section['CRN'] + " Professor: " + section['professor'] + " Rating: " + str(section['profRating']) + " # of ratings: " + str(section['numReviews']))  # Print each section's information
            print("\n")
