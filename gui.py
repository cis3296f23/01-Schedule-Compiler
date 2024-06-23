import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkinter import *
from tkinter import ttk
import temple_requests
import algo
from algo import Schedule
from plotting import draw
from text_redirection import TextRedirector
import sys
from threading import Thread, Lock
from custom_thread import Custom_Thread
import customtkinter
import re
import platform

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
        if platform.system() == 'Windows':
            self.__root.state('zoomed')
        ttk.Label(self.__root, text = 'Schedule Compiler', font='Fixedsys 35 bold', justify="center", background='#3498db', foreground='white').pack(padx=5,pady=5)
        self.__style = ttk.Style()
        self.__style.configure('TFrame', background='#ecf0f1')

        self.main_frame=customtkinter.CTkScrollableFrame(self.__root, fg_color = 'transparent')
        self.main_frame.pack(side="top",fill="both", expand=1, anchor="center")
        #Credit to Yazan Al Hariri for up and down key bindings (https://stackoverflow.com/questions/78051328/how-to-scroll-down-in-ctkscrollableframe-using-arrow-keys-in-custom-tkinter)
        self.main_frame.bind_all("<Up>", lambda event: self.main_frame._parent_canvas.yview("scroll", -25, "units"), add="+")
        self.main_frame.bind_all("<Down>", lambda event: self.main_frame._parent_canvas.yview("scroll", 25, "units"), add="+")
        self.added_courses = []
        self.course_info = dict()
        self.prof_rating_cache = dict()
        self.unavail_times = Schedule()
        self.__style = ttk.Style()
        self.__style.configure('Green.TButton', font=('Helvetica', 12, 'bold'), background='#2ecc71',
                               foreground='black')
        self.__style.configure('Red.TButton', font=('Helvetica', 12, 'bold'), background='#e74c3c', foreground='black')
        self.__style.configure('Header.TLabel', font = ('Courier',18,'bold'))
        self.__style.configure('Custom.TLabel', font=('Arial', 11), foreground='black')
        self.degr_prog_lock = Lock()
        self.keyword_search_lock = Lock()
        self.collect_user_input_lock = Lock()
        self.compile_sched_lock = Lock()
        self.draw_sched_lock = Lock()

        self.build_degr_prog_frame(self.main_frame)
        self.build_courses_frame(self.main_frame)
        self.build_unavail_time_frame(self.main_frame)
        self.build_compile_schedule_frame(self.main_frame)
    
    def build_degr_prog_frame(self, master):
        """
        Builds the degree program selection and entry frame
        @param master : parent frame
        """
        self.custom_font_bold = ("Arial", 15, "bold")
        self.custom_font = ("Arial", 15)
        #degree program selection gui
        self.prog_frame = customtkinter.CTkFrame(master=master, border_width=2, corner_radius=10,fg_color = "transparent")
        self.prog_frame.grid(row=0, padx = 10, pady=10)

        ttk.Label(self.prog_frame,text='Degree Program',font = self.custom_font_bold,).grid(row=0, padx=5, pady=5)
        customtkinter.CTkLabel(self.prog_frame,text='Note: Select a degree program if you would like to see a list of courses in the curriculum \n (can type to narrow down, no worries if your program is not in the list)',font = ("Arial", 12, "italic")).grid(row=1, padx=2, pady=2)
        self.error_otpt = ""
        self.degr_prog_to_url = temple_requests.get_degr_progs()
        self.all_degr_progs = list(self.degr_prog_to_url.keys())
        if self.all_degr_progs and "Try connecting" in self.all_degr_progs[0]:
            self.error_otpt+=self.all_degr_progs[0]
        self.all_degr_progs_var = Variable()
        self.all_degr_progs_var.set(self.all_degr_progs)
        self.degr_prog_entry = customtkinter.CTkEntry(self.prog_frame, width=250, placeholder_text="Enter Degree Program")
        self.degr_prog_entry.grid(row=2)
        self.degr_prog_listbox = Listbox(self.prog_frame,listvariable=self.all_degr_progs_var, selectmode='single', width=70, height=10)
        self.degr_prog_listbox.grid(row=3, pady=15, padx=15)
        self.degr_prog_listbox.bind('<<ListboxSelect>>',self.pick_degr_prog)
        self.degr_prog_entry.bind('<KeyRelease>', lambda filler : self.narrow_search(filler,entry=self.degr_prog_entry, lst=self.all_degr_progs, lstbox=self.degr_prog_listbox))

    def build_courses_frame(self, master):
        """
        Builds the frame that allows input, selection, and modifying of courses
        @param master : parent frame
        """
        self.courses_f = customtkinter.CTkFrame(master=master, border_width=0, corner_radius=10, fg_color = "#DDDDDD", height = 500, width = 500)
        self.courses_f.grid(row=1, padx=15,pady=15, sticky="nsew")
        self.specifications_frame = customtkinter.CTkFrame(master=self.courses_f, width=200, height=200, fg_color = "transparent", border_width = 2, corner_radius=10)
        self.specifications_frame.grid(row=3, column=0, padx=5, pady=5)
        #semester selection
        customtkinter.CTkLabel(self.specifications_frame, text="Semester:", fg_color="transparent", font = self.custom_font_bold).grid(row=0, column=0, padx=5, pady=(15,5))
        self.term_to_code = temple_requests.get_param_data_codes('getTerms')
        self.terms = list(self.term_to_code.keys())
        self.term_combobox = ttk.Combobox(self.specifications_frame, values=self.terms, state="readonly")
        #self.term_combobox.set(self.terms[i])
        if "Try connecting" in self.terms[0]:
            self.error_otpt+=self.terms[0]
        self.term_combobox.grid(row=1, padx=15, pady=5)
        self.term_combobox.bind('<<ComboboxSelected>>', self.on_term_or_campus_selected)
        #select a campus
        customtkinter.CTkLabel(self.specifications_frame, text="Campus:",fg_color="transparent", font = self.custom_font_bold).grid(row=2,column=0, padx=10)
        self.campus_to_code = temple_requests.get_param_data_codes('get_campus')
        self.campuses = list(self.campus_to_code.keys())
        self.campus_combobox = ttk.Combobox(self.specifications_frame, values=self.campuses, state="readonly")
        if 'Main' in self.campuses:
            self.campus_combobox.set('Main')
        else:
            self.campus_combobox.set(self.campuses[0])
            if "Try connecting" in self.campuses[0]:
                self.error_otpt+=self.campuses[0]
        self.campus_combobox.grid(row=4, column=0, padx=15, pady=(5,30))
        self.campus_combobox.bind('<<ComboboxSelected>>', self.on_term_or_campus_selected)
        #Credit entry
        self.credit_label = customtkinter.CTkLabel(self.specifications_frame, text="Enter max # of credits (leave blank for 18)", fg_color="transparent", font = self.custom_font_bold).grid(row=5)
        self.max_cred_entry = customtkinter.CTkEntry(self.specifications_frame, width=50)
        self.max_cred_entry.grid(row=6, padx=5, pady=5)
        #course entry gui
        self.courses_frame = customtkinter.CTkFrame(master=self.courses_f, border_width=2,corner_radius=10)
        self.courses_frame.grid(row=3, column=1, padx=10, pady=10)
        self.courses_shown = []
        customtkinter.CTkLabel(self.courses_f, text='Course Selection', font = self.custom_font_bold, fg_color="transparent").grid(row=0, column=1, padx=10, pady=10)
        customtkinter.CTkLabel(self.courses_f,text= "Options: 1. Enter your desired course in SUBJ #### (e.g. CIS 0823) or attribute (e.g. GA) format and press Enter key or Add button below to add\n2. Enter keywords (not in the format specified above) to search and press Enter or the Search button to see the subject and code\n(Notes: 1. Add by top priority to least priority if desired\n2. Can filter through courses if there any shown below \n3. Can add course even if not in list below)", fg_color="transparent", font = ("Arial", 12, "italic")).grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky = "w")
        self.course_entry=customtkinter.CTkEntry(self.courses_frame,placeholder_text="Enter keywords to search or the subject code and number combo if you already know", width=500)
        self.course_entry.grid(row=1, padx=15, pady=15)
        self.courses_shown_var = Variable()
        self.courses_shown_var.set(self.courses_shown)
        self.course_lstbox = Listbox(self.courses_frame, selectmode='single', listvariable=self.courses_shown_var, width=70, height=10)
        self.course_lstbox.grid(row=2, padx=10, pady=10)
        self.course_lstbox.bind('<<ListboxSelect>>',lambda filler : self.insert_selection(filler, entry=self.course_entry,lstbox=self.course_lstbox))
        self.course_entry.bind('<KeyRelease>',lambda filler : self.narrow_search(filler, entry=self.course_entry, lst=self.courses_shown,lstbox=self.course_lstbox))
        self.course_entry.bind('<Return>',self.add_course_to_list)
        customtkinter.CTkButton(self.courses_frame, text="Search for Course", command=lambda:self.search_for_keywords(lst=self.courses_shown,lst_var=self.courses_shown_var,entry=self.course_entry)).grid(row=3)
        #buttons to add
        customtkinter.CTkButton(self.courses_frame, text="Add Course", command=lambda: self.add_course_to_list(event=None)).grid(row=4,padx=10,pady=10)
        #Selected Courses
        self.remove_frame = customtkinter.CTkFrame(master=self.courses_f, border_width=2, corner_radius=10, fg_color=master.cget("fg_color"), width = 200, height=300)
        self.remove_frame.grid(row=3, column=3, padx=10, pady=10)
        # Configure row weight for equal spacing
        self.courses_f.rowconfigure(0, weight=1)
        #listbox for displaying added courses
        customtkinter.CTkLabel(self.remove_frame, text="Selected Courses", fg_color="transparent", font = self.custom_font_bold).grid(row=0, padx=10, pady=15)
        self.added_courses_listbox = Listbox(self.remove_frame, width=15, height=10)
        self.added_courses_listbox.grid(row=1, padx=10, pady=5)
        #Remove courses from the list
        customtkinter.CTkButton(
            self.remove_frame, text="Remove Course",
            command=lambda: self.remove_item_from_lstbox(lstbox=self.added_courses_listbox, lst=self.added_courses)).grid(row=3, padx=10, pady=15)
        customtkinter.CTkButton(
            self.remove_frame, text="Clear Courses",
            command=lambda: self.clear_lstbox(lstbox=self.added_courses_listbox, lst=self.added_courses)).grid(row=4, padx=10, pady=5)

    def build_unavail_time_frame(self, master):
        """
        Builds the frame that allows for adding and removing of unavailable times
        @param master : parent frame
        """
        self.unavailable_frame = customtkinter.CTkFrame(master=master, width=200, height=200, border_width = 0, corner_radius=10, fg_color = "#DDDDDD")
        self.unavailable_frame.grid(row=4, padx=5, pady=5, sticky = "nsew")
        # Configure column weights for equal spacing
        self.unavailable_frame.columnconfigure(0, weight=1)
        self.unavailable_frame.columnconfigure(1, weight=1)
        # Configure row weights
        self.unavailable_frame.rowconfigure(0, weight=1)
        self.date_time_frame = customtkinter.CTkFrame(master=self.unavailable_frame, width=200, height=200, border_width = 2, corner_radius=10, fg_color = "transparent")
        self.date_time_frame.grid(row=0, padx=(50,0), pady=15)
        #day and time input
        customtkinter.CTkLabel(self.date_time_frame, text="Unavailable Times", fg_color="transparent", font = self.custom_font_bold).grid(row=0, column=0, padx=5, pady=(15,0))
        customtkinter.CTkLabel(self.date_time_frame, text="Enter days and times NOT available:", fg_color="transparent", font = ("Arial", 12, "italic")).grid(row=1, padx=5)
        # Days of the week selection
        customtkinter.CTkLabel(self.date_time_frame, text="Select Day:", bg_color="transparent", font = ("Arial", 15, "bold")).grid(row=2, padx=5, pady=5)
        self.days_dropdown = ttk.Combobox(self.date_time_frame, values=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'] , state='readonly', width=20)
        self.days_dropdown.set('Sunday')
        self.days_dropdown.grid(row=3, padx=5)
        # Times selection
        self.time_frame = customtkinter.CTkFrame(master=self.date_time_frame)
        self.time_frame.grid(row=18, padx=5, pady=5)
        #self.time_label = ttk.Label(master, text="Select Time Range:").grid(row=18, column=0, columnspan=2)
        self.time_label = customtkinter.CTkLabel(self.time_frame, text="Select Time Range:", fg_color="transparent", font = ("Arial", 15, "bold"))
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
        # Add button to list of unavailable times
        customtkinter.CTkButton(self.date_time_frame, text="Add Time", command=self.add_timeslot, width=15).grid(row=21, padx=5, pady=(5,15))
        self.selected_times_frame = customtkinter.CTkFrame(master=self.unavailable_frame, width=200, height=200, border_width = 2, corner_radius=10, fg_color = "transparent")
        self.selected_times_frame.grid(row=0, column=1, padx=(0,50), pady=5)
        #List of exluded times
        customtkinter.CTkLabel(self.selected_times_frame, text="Excluded date and time", font = ("Arial", 15, "bold"), fg_color="transparent").grid(row=0, padx=5, pady=5)
        self.day_and_time_slots = []
        self.day_and_time_slots_var = Variable()
        self.day_and_time_slots_var.set(self.day_and_time_slots)
        self.times_unavail_lstbox = Listbox(self.selected_times_frame,listvariable=self.day_and_time_slots_var,selectmode='single',width=20,height=5)
        self.times_unavail_lstbox.grid(row=21, padx=5, pady=5)
        # Remove time and date entry button
        customtkinter.CTkButton(self.selected_times_frame, text="Remove Time", command=self.remove_timeslot, width=25).grid(row=22, padx=5, pady=(5,15))

    def build_compile_schedule_frame(self, master):
        """
        Builds the frame for schedule compilation and output of progress
        @param master : parent frame
        """
        #compilation of schedules
        self.compilation_frame = customtkinter.CTkFrame(master=master, border_width = 2, corner_radius=10, fg_color = "transparent")
        self.compilation_frame.grid(row=5, padx=5, pady=5)

        customtkinter.CTkButton(self.compilation_frame, width=28, text="Compile Possible Schedules", font=("Fixedsys", 25, "bold"), command=self.compile_schedules).grid(row=0, padx=10, pady=(15,0))
        self.output = Text(self.compilation_frame, width=50, height=10, background='#ecf0f1', wrap=WORD, state='disabled')
        self.output.grid(row=27,column=0, padx=15, pady=(15,50), sticky = "s")
        sys.stdout = TextRedirector(self.output,'stdout')
        print(self.error_otpt)
        
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
            #if the lstbox is the course listbox, then the selection is parsed to be 'SUBJ ####' format
            if lstbox==self.course_lstbox:
                first_space_ind = selection.find(' ')
                second_space_ind = -1
                if first_space_ind!=-1:
                    second_space_ind = selection.find(' ',first_space_ind+1)
                if second_space_ind:
                    selection = selection[:second_space_ind]
            entry.insert(0,selection)
            return selec_ind, selection
        return None,None

    def pick_degr_prog(self,event:Event):
        """
        Updates degree program entry box with selected degree program and starts a thread that updates the course listbox with the curriculum of the selected degree program
        @param event : implicit parameter entered when a function is called as part of an event bind
        """
        #updates degree program entry box
        selec_ind, selection = self.insert_selection(None,self.degr_prog_entry,self.degr_prog_listbox)
        #updates course selection listbox if a degree program was selected
        if selec_ind:
            Thread(target=self.update_course_lstbox,args=[selection]).start()
            
    def update_course_lstbox(self,selection):
        """
        Updates the course listbox with curriculum corresponding to the value of selection
        @selection : str of selected degree program
        """
        #see why this logic is clearing the courses outputted by the keyword search
        self.degr_prog_lock.acquire()
        curric = Variable()
        self.courses_shown = temple_requests.get_curric(self.degr_prog_to_url[selection])
        num_courses = len(self.courses_shown)
        if "Try connecting" not in self.courses_shown[0]:
            for c in range(num_courses):
                self.courses_shown[c][0]=self.courses_shown[c][0].replace('\xa0',' ')
                self.courses_shown[c]=' '.join(self.courses_shown[c])
        curric.set(self.courses_shown)
        self.course_lstbox.config(listvariable=curric) 
        self.degr_prog_lock.release()

    def add_course_to_list(self,event:Event):
        """
        Adds course entered in course entry to the added courses listbox
        """
        selected_course = self.course_entry.get()
        selected_course_added = selected_course in self.added_courses_listbox.get(0, END)
        if selected_course and not selected_course_added and bool(re.match(r"(^[A-Z]{2,4} \d{4}$)|(^[A-Z]{2}$)",selected_course)):
            self.added_courses_listbox.insert(END, selected_course)
            self.added_courses.append(selected_course)
            self.course_entry.configure(placeholder_text="Enter kewords to search or Course Subject and Number if you already know")
        elif not selected_course:
            self.course_entry.configure(placeholder_text="Cannot add blank course.")
        elif selected_course_added:
            self.course_entry.configure(placeholder_text="Course already added.")
        else:
            self.search_for_keywords(self.courses_shown,self.courses_shown_var,self.course_entry)
        self.course_entry.delete(0,END)
        self.__root.focus_set()

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
    
    def search_for_keyword_thread(self,lst:list[str],lst_var:Variable,term:str,keywords:str):
        """
        Callback for thread to fetch courses from a keyword search in TUPortal's schedule service
        @param lst : list that will store the courses 
        @param lst_var : tkinter list variable
        @param term : semester selected to schedule for
        @param keywords
        """
        self.keyword_search_lock.acquire()
        lst.clear()
        lst.append("Searching...")
        lst_var.set(lst)
        self.course_lstbox.config(listvariable=lst_var)
        results = temple_requests.get_courses_from_keyword_search(self.term_to_code[term],keywords)
        lst.clear()
        lst.extend([f"{subj_code} {title}" for subj_code, title in results])
        lst_var.set(lst)
        self.course_lstbox.config(listvariable=lst_var)
        self.keyword_search_lock.release()

    def search_for_keywords(self,lst:list[str],lst_var:Variable,entry:Entry):
        """
        Searches the TUPortal scheduling service for the keywords entered in the specified entry widget
        @param lst : list to store results in
        @param lst_var : Tkinter list variable to change
        @param entry : the entry widget to get the keywords from
        """
        term = self.term_combobox.get()
        if not term:
            lst_var.set(["You must select the semester you want to schedule classes for."])
            self.course_lstbox.config(listvariable=lst_var)
            return
        keywords = entry.get()
        if keywords:
            Thread(target=self.search_for_keyword_thread,args=(lst,lst_var,term,keywords)).start()

    def clear_lstbox(self, lstbox:Listbox,lst:list[str]):
        """
        Clears the contents of the given Listbox
        @param lstbox : Listbox to clear
        @param lst : lst associated to the Listbox
        """
        for i in range(len(lst)-1,-1,-1):
            lstbox.delete(i)
            lst.pop(i)

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
            if self.unavail_times.add_timeslot(selected_day[0].lower()+selected_day[1:],int(str(start_hour)+str(start_minute)),int(str(end_hour)+str(end_minute)),""):
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

    def compile_schedules_thread(self):
        """
        Collects information for the user's desired courses for the selected semester and times they are not available and compiles a schedule
        @return -1 if exits with error, positive number otherwise
        """
        with self.collect_user_input_lock:
            term = self.term_combobox.get()
            if not term:
                print("You must select the semester you want to schedule classes for.")
                return []
            entered_max_credits = self.max_cred_entry.get()
            if entered_max_credits and not entered_max_credits.isnumeric():
                print("You must enter a number for maximum credit limit or leave it blank for 18.")
                return []
            campus_code = self.campus_to_code[self.campus_combobox.get()]
            course_info = dict(self.course_info)
            prof_rating_cache = dict(self.prof_rating_cache)
            added_courses = list(self.added_courses)
            unavail_times = self.unavail_times.copy()
        self.compile_sched_lock.acquire()
        print("Starting schedule compilation...")
        for course in added_courses:
            subj, course_num, attr = '', '', ''
            if course[-1].isnumeric():
                i = 0
                while i<len(course) and course[i]!=' ':
                    subj+=course[i]
                    i+=1
                if i<len(course) and course[i]==' ':
                    course_num+=course[i+1:]
            else:
                attr = course
            print(f"Processing course: {subj} {course_num} {attr}")
            if temple_requests.get_course_sections_info(course_info,term,self.term_to_code[term],subj,course_num,attr,campus_code,prof_rating_cache)=="":
                if term not in self.course_info:
                    self.course_info[term]=dict()
                if campus_code not in self.course_info[term]:
                    self.course_info[term][campus_code]=dict()
                self.course_info[term][campus_code][course]=course_info[term][campus_code][course]
        for prof in prof_rating_cache:
            if prof not in self.prof_rating_cache:
                self.prof_rating_cache[prof] = prof_rating_cache[prof]
        valid_rosters = algo.build_all_valid_rosters(course_info,term,campus_code,added_courses, unavail_times, 18 if not entered_max_credits else int(entered_max_credits))
        if valid_rosters:
            print("Schedule compilation complete. Building the rosters...")
            """for i, roster in enumerate(self.valid_rosters):
                print(f"Valid Roster {i + 1}:")
                print(roster)  # Print the schedule
                print("\nSections in this Schedule:")
                for j, section in enumerate(roster.sections):
                    print(str(j+1) + ". " + section['name'] + " CRN: " + section['CRN'] + " Professor: " + section['professor'] + " Rating: " + str(section['profRating']) + " # of ratings: " + str(section['numReviews']))  # Print each section's information
                print("\n")"""
        else:
            print("No valid rosters.")
        print('Done')
        self.compile_sched_lock.release()
        return valid_rosters

    def display_prev_sched(self,event=None):
        """
        Navigates to the next schedule display
        @param event : filler variable
        """
        self.roster_page_num-=1
        self.sched_frames[(self.roster_page_num-1)%len(self.sched_frames)].tkraise()

    def display_next_sched(self,event=None):
        """
        Navigates to the previous schedule display
        @param event : filler variable
        """
        self.roster_page_num+=1
        self.sched_frames[(self.roster_page_num-1)%len(self.sched_frames)].tkraise()
    
    def exit_sched_display(self,event=None):
        """
        Exits the schedule display and destroys the frames
        @param event : filler variable
        """
        for frame in self.sched_frames:
            frame.destroy()
        self.sched_frames=[]
        self.draw_sched_lock.release()

    def compile_schedules(self,event=None):
        """
        Creates thread for schedule compilation to be executed separate from the GUI
        """
        thread = Custom_Thread(callback1=self.compile_schedules_thread,callback2=self.draw_schedules)
        thread.start()
    
    def draw_schedules(self,valid_rosters):
        """
        Creates frames, calls their draw function to plot the schedule graph on them, and reveals the first graph if there are any
        @param valid_rosters : generated list of schedules
        """
        self.draw_sched_lock.acquire()
        self.sched_frames = []
        self.roster_page_num=1
        for i in range(len(valid_rosters)):
            figure = Figure(figsize=(18,7))
            frame=Sched_Frame(self.main_frame,self,i+1,len(valid_rosters))
            self.sched_frames.append(frame)
            frame.grid(row=0,column=0,sticky="nsew")
            frame.draw_schedule(figure,valid_rosters,i)
        if self.sched_frames:
            self.sched_frames[0].tkraise()

class Sched_Frame(customtkinter.CTkFrame):
    """
    Frame for displaying and navigating through schedule graphs
    """
    def __init__(self,parent,controller:GUI,page_num:int,num_valid_rosters:int):
        self.controller = controller
        customtkinter.CTkFrame.__init__(self,parent)
        if num_valid_rosters>1:
            nav_frame = customtkinter.CTkFrame(self)
            nav_frame.pack(side="top",anchor="center",pady=5)
            if page_num>1:
                customtkinter.CTkButton(nav_frame, text="Previous", command=controller.display_prev_sched).pack(side="left",anchor="center",padx=5)
            if page_num<num_valid_rosters:
                customtkinter.CTkButton(nav_frame, text="Next", command=controller.display_next_sched).pack(side="left",anchor="center",padx=5)
        exit_frame = customtkinter.CTkFrame(self)
        exit_frame.pack(side="top",anchor="center")
        customtkinter.CTkButton(exit_frame,text="Exit",command = controller.exit_sched_display).pack(side="bottom",anchor="center")
    
    def draw_schedule(self, figure:Figure, valid_rosters,i):
        """
        Plots the schedule on itself
        @param figure
        @param valid_rosters : list of schedules
        @param i : index within valid_rosters
        """
        axes = figure.add_subplot(121)
        draw(axes,valid_rosters,i)
        figure.text(0.5,0.3,s=self.get_course_info(valid_rosters,i))
        canv = FigureCanvasTkAgg(figure,self)
        canv.draw()
        canv.get_tk_widget().pack(side="bottom",fill='both',expand=True)
        toolbar = NavigationToolbar2Tk(canv, self)
        toolbar.update()
        canv._tkcanvas.pack(side="top", fill="both", expand=True)
        canv.get_tk_widget().bind("<Left>",self.controller.display_prev_sched)
        canv.get_tk_widget().bind("<Right>",self.controller.display_next_sched)
        canv.get_tk_widget().bind("<Escape>",self.controller.exit_sched_display)
    
    def get_course_info(self,schedules,i):
        """
        Parses sections chosen for the potential schedule to show section info in text in each tab in a textbox
        @param schedules : list of potential schedules
        @param i : current index in schedules
        """
        course_info_str = f'Chart {i + 1}\n'
        for section in schedules[i].sections:
            course_info = f"{section['name']} CRN: {section['CRN']} Professor: {section['professor']} Rating: {section['profRating']} # of Reviews: {section['numReviews']}\n"
            course_info_str += course_info
        course_info_str += '\n'
        return course_info_str