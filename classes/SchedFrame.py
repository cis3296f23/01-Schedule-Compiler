import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import customtkinter

from draw import draw

class SchedFrame(customtkinter.CTkFrame):
    """
    Frame for displaying and navigating through schedule graphs
    """
    # Keep import here to resolve circular import issue
    from classes.GUI import GUI
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