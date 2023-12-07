from tkinter import *
from tkinter import ttk
import temple_requests
import algo
from algo import Schedule
from text_redirection import TextRedirector
import sys,threading, multiprocessing
import customtkinter

class GUI():
    def __init__(self,root:Tk):
        """
        Initializes the title, screen, and frames used
        """
        self.running = True
        self.__root = root
        self.__root.title('Schedule Compiler')
        customtkinter.set_appearance_mode("light")
        root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(),root.winfo_screenheight()))
        #Can pick out style later
        title_label = ttk.Label(self.__root, text = 'Schedule Compiler', font='Fixedsys 35 bold', justify=CENTER, background='#3498db', foreground='white')
        title_label.pack(padx=5,pady=5)
        self.__style = ttk.Style()
        self.__style.configure('TFrame', background='#ecf0f1')

        main_frame=customtkinter.CTkFrame(self.__root, fg_color = 'transparent')
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
        second_frame = customtkinter.CTkFrame(canv,  fg_color = 'transparent')
        second_frame.pack(fill=BOTH,expand=1)
        canv.create_window((int(main_frame.winfo_screenwidth()/4),0), window=second_frame, anchor = "nw")
        self.added_courses = []
        self.course_info = dict()
        self.prof_rating_cache = dict()
        self.unavail_times = Schedule()
        self.__style = ttk.Style()
        self.__style.configure('Green.TButton', font=('Helvetica', 12, 'bold'), background='#2ecc71',
                               foreground='black')
        self.__style.configure('Red.TButton', font=('Helvetica', 12, 'bold'), background='#e74c3c', foreground='black')
        self.__style.configure('Header.TLabel', font = ('Courier',18,'bold'))
        self.__style.configure('Custom.TLabel', font=('Arial', 12), foreground='#34495e')

        self.build_general_frame(second_frame)
    
    def build_general_frame(self,master):
        """
        Builds the GUI
        @param master : root application
        """
        #degree program selection gui
        self.prog_frame = customtkinter.CTkFrame(
            master=master,
            border_width=2,
            corner_radius=10,
            fg_color = "transparent",
        )
        self.prog_frame.grid(row=0, padx = 10, pady=10)

        self_prog_label = customtkinter.CTkLabel(self.prog_frame,
                                    text='Degree Program',
                                    bg_color = "transparent")
        self_prog_label.grid(row=0, padx=5, pady=5)
        self.degr_prog_to_url = temple_requests.get_degr_progs()
        self.all_degr_progs = list(self.degr_prog_to_url.keys())
        self.all_degr_progs_var = Variable()
        self.all_degr_progs_var.set(self.all_degr_progs)
        self.degr_prog_entry = customtkinter.CTkEntry(self.prog_frame,
                                                      width=250,
                                                      placeholder_text="Enter Degree Program")
        self.degr_prog_entry.grid(row=1)
        self.degr_prog_listbox = Listbox(self.prog_frame,
                                         listvariable=self.all_degr_progs_var,
                                         selectmode='single',
                                         width=70,
                                         height=10)
        self.degr_prog_listbox.grid(row=2, pady=15, padx=15)
        self.degr_prog_listbox.bind('<<ListboxSelect>>',self.pick_degr_prog)
        self.degr_prog_entry.bind('<KeyRelease>', lambda filler : self.narrow_search(filler,entry=self.degr_prog_entry, lst=self.all_degr_progs, lstbox=self.degr_prog_listbox))

        self.courses_f = customtkinter.CTkFrame(master=master,
                                                    border_width=0,
                                                    corner_radius=10,
                                                    fg_color = "transparent",
                                                    )
        self.courses_f.grid(row=1, padx=15,pady=15)
        #course entry gui
        self.courses_frame = customtkinter.CTkFrame(master=self.courses_f,
                                                    border_width=2,
                                                    corner_radius=10,
                                                    fg_color = "transparent",
                                                    width = 150,
                                                    height = 100
                                                    )
        self.courses_frame.grid(row=0, column=0, padx=5, pady=5)
        self.curr_curric = []
        self.courses_label = ttk.Label(self.courses_frame,text="Available Courses")
        self.courses_label.grid(row=0, column=0, padx = 15, pady=15)
        # Enter your course and press Enter key or button below to add (Notes: 1. add by top priority to least priority if desired 2. can type to search 3. can add course even if not in list):").grid(row=3)
        self.course_entry=customtkinter.CTkEntry(self.courses_frame,
                                                 width=250,
                                                 placeholder_text= "Enter Course Name"
                                                 )
        self.course_entry.grid(row=1, padx=15, pady=5)
        self.curr_curric_var = Variable()
        self.curr_curric_var.set(self.curr_curric)
        self.course_lstbox = Listbox(self.courses_frame,
                                     selectmode='single',
                                     listvariable=self.curr_curric_var,
                                     width=15,
                                     height=10)
        self.course_lstbox.grid(row=2, padx=10, pady=10)
        self.course_lstbox.bind('<<ListboxSelect>>',lambda filler : self.insert_selection(filler, entry=self.course_entry,lstbox=self.course_lstbox))
        self.course_entry.bind('<KeyRelease>',lambda filler : self.narrow_search(filler, entry=self.course_entry, lst=self.curr_curric,lstbox=self.course_lstbox))
        self.course_entry.bind('<Return>',self.add_course_to_list)
        #buttons to add
        self.add_course_btn = customtkinter.CTkButton(self.courses_frame, text="Add Course", command=lambda: self.add_course_to_list(event=None),)
        self.add_course_btn.grid(row=3, padx=10,pady=10)

        #Selected Courses
        self.remove_frame = customtkinter.CTkFrame(master=self.courses_f,
                                                   border_width=2,
                                                   corner_radius=10,
                                                   fg_color = "transparent",
                                                   width = 100,
                                                   height=150)
        self.remove_frame.grid(row=0, column=1, padx=50, pady=5)
        #listbox for displaying added courses
        self.remove_label = customtkinter.CTkLabel(self.remove_frame, text="Selected Courses", fg_color="transparent")
        self.remove_label.grid(row=0, padx=10, pady=10)
        self.added_courses_listbox = Listbox(self.remove_frame, width=15, height=10)
        self.added_courses_listbox.grid(row=1, padx=10)
        #Remove
        self.remove_course_btn = customtkinter.CTkButton(
            self.remove_frame, text="Remove Course",
            command=lambda: self.remove_item_from_lstbox(lstbox=self.added_courses_listbox, lst=self.added_courses))
        self.remove_course_btn.grid(row=3, padx=10, pady=10)

        #semester selection
        ttk.Label(master, text="Select the semester to create a schedule for:").grid(row=9)
        self.term_to_code = temple_requests.get_param_data_codes('getTerms')
        self.terms = list(self.term_to_code.keys())
        self.term_combobox = ttk.Combobox(master, values=self.terms, state="readonly")
        self.term_combobox.set(self.terms[1])
        self.term_combobox.grid(row=10)
        self.term_combobox.bind('<<ComboboxSelected>>', self.on_term_or_campus_selected)
        #select a campus
        ttk.Label(master, text="Select a Campus:").grid(row=11)
        self.campus_to_code = temple_requests.get_param_data_codes('get_campus')
        self.campuses = list(self.campus_to_code.keys())
        self.campus_combobox = ttk.Combobox(master, values=self.campuses, state="readonly")
        self.campus_combobox.set('Main')
        self.campus_combobox.grid(row=12)
        self.campus_combobox.bind('<<ComboboxSelected>>', self.on_term_or_campus_selected)
        #Credit entry
        ttk.Label(master, text="Enter the maximum number of credits you would like to take:").grid(row=13)
        self.max_cred_entry = customtkinter.CTkEntry(master, width=50)
        self.max_cred_entry.grid(row=14)
        self.output= Text(master, width = 50, height=10)
        #day and time input
        ttk.Label(master, text="Add days and times you are NOT available:").grid(row=15)
        # Days of the week selection
        ttk.Label(master, text="Select Day:").grid(row=16)
        self.days_dropdown = ttk.Combobox(master, values=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'] , state='readonly', width=20)
        self.days_dropdown.set('Sunday')
        self.days_dropdown.grid(row=17)
        # Times selection
        self.time_frame = customtkinter.CTkFrame(master=master)
        self.time_frame.grid(row=18, padx=5, pady=5)
        #self.time_label = ttk.Label(master, text="Select Time Range:").grid(row=18, column=0, columnspan=2)
        self.time_label = customtkinter.CTkLabel(self.time_frame, text="Select Time Range", fg_color="transparent")
        self.time_label .grid(row=0, padx=10,pady=10)
        start_time_frame = ttk.Frame(self.time_frame)
        start_time_frame.grid(row=1, column=0)
        end_time_frame = ttk.Frame(self.time_frame)
        end_time_frame.grid(row=2, column=0)
        master.grid_columnconfigure(0, weight=1)
        # Hour selection
        hours = [str(i).zfill(2) for i in range(0, 24)]
        self.start_hour_dropdown = ttk.Combobox(start_time_frame, values=hours, state="readonly", width=3)
        self.start_hour_dropdown.pack(side='left', anchor='w')
        self.end_hour_dropdown = ttk.Combobox(end_time_frame, values=hours, state="readonly", width=3)
        self.end_hour_dropdown.pack(side='left', anchor='w')
        # Minute selection
        minutes = [str(i).zfill(2) for i in range(0, 60, 5)]
        self.start_minute_dropdown = ttk.Combobox(start_time_frame, values=minutes, state="readonly", width=3)
        self.start_minute_dropdown.pack(side='left', anchor='w')
        self.end_minute_dropdown = ttk.Combobox(end_time_frame, values=minutes, state="readonly", width=3)
        self.end_minute_dropdown.pack(side='left', anchor='w')
        # Add and remove button to add/remove selected time
        self.add_time_btn = customtkinter.CTkButton(master, text="Add Time", command=self.add_timeslot, width=15)
        self.add_time_btn.grid(row=21)
        self.remove_time_btn = customtkinter.CTkButton(master, text="Remove Time", command=self.remove_timeslot, width=15)
        self.remove_time_btn.grid(row=22)
        self.day_and_time_slots = []
        self.day_and_time_slots_var = Variable()
        self.day_and_time_slots_var.set(self.day_and_time_slots)
        self.times_unavail_lstbox = Listbox(master,listvariable=self.day_and_time_slots_var,selectmode='single',width=30,height=10)
        self.times_unavail_lstbox.grid(row=23)
        #compilation of schedules
        self.compile_button =customtkinter.CTkButton(
            master, width=28, text="Compile Possible Schedules", command=self.schedule_compiler_thread)
        self.compile_button.grid(row=26)
        self.output = Text(master, width=50, height=10, background='#ecf0f1', wrap=WORD, state='disabled')
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

    def remove_item_from_lstbox(self,lstbox:Listbox,lst:list[str]):
        """
        Removes selected course in the listbox from that listbox and from the corresponding list
        @return item : removed data, None if no item was selected for removal
        """
        selected_index = lstbox.curselection()
        if selected_index:
            item = lstbox.get(selected_index)
            lstbox.delete(selected_index)
            lst.pop(selected_index[0])
            return item

    def add_timeslot(self):
        """
        Adds the unavailable time entered to the corresponding listbox and to self.unavail_times
        """
        selected_day = self.days_dropdown.get()
        start_hour = self.start_hour_dropdown.get()
        start_minute = self.start_minute_dropdown.get()
        end_hour = self.end_hour_dropdown.get()
        end_minute = self.end_minute_dropdown.get()
        if selected_day and start_hour and start_minute and end_hour and end_minute:
            if self.unavail_times.add_timeslot(selected_day[0].lower()+selected_day[1:],int(str(start_hour)+str(start_minute)),int(str(end_hour)+str(end_minute))):
                self.day_and_time_slots.append(selected_day + ' ' + start_hour + start_minute + '-' + end_hour + end_minute)
                day_and_time_slots_var = Variable()
                day_and_time_slots_var.set(self.day_and_time_slots)
                self.times_unavail_lstbox.config(listvariable=day_and_time_slots_var)
        else:
            print("Please select all components of the time.")
    
    def remove_timeslot(self):
        """
        Removes the timeslot selected in the listbox from the listbox and from self.unavail_times
        """
        timeslot = self.remove_item_from_lstbox(self.times_unavail_lstbox,self.day_and_time_slots)
        if timeslot:
            space_ind = timeslot.find(' ')
            day = timeslot[0].lower()+timeslot[1:space_ind]
            dash_ind = timeslot.find('-',space_ind+1)
            self.unavail_times.remove_timeslot(day,int(timeslot[space_ind+1:dash_ind]),int(timeslot[dash_ind+1:]))

    def compile_schedules(self):
        """
        Collects information for the user's desired courses for the selected semester and 
        """
        print("Start schedule compilation process...")
        for course in self.added_courses:
            subj, course_num, attr = '', '', ''
            #can use regex later on to check if valid course was entered (Two letters for attribute or Subj course_num format)
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
            temple_requests.get_course_sections_info(self.course_info,self.term_to_code[self.term_combobox.get()],subj,course_num,attr,self.campus_to_code[self.campus_combobox.get()],self.prof_rating_cache)
        valid_rosters = algo.build_all_valid_rosters(self.course_info,self.added_courses, self.unavail_times)
        print("Schedule compilation complete. Building the rosters...")
        multiprocessing.Process(target=algo.plot_schedule, args=(valid_rosters,)).start()
        multiprocessing.Process(target=algo.display_course_info, args=(valid_rosters,)).start()


    def schedule_compiler_thread(self):
        """
        Creates thread for schedule compilation to be executed separate from the GUI
        """
        threading.Thread(target=self.compile_schedules).start()
