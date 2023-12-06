from gui import GUI
from tkinter import *
import customtkinter

if __name__=='__main__':
    root = customtkinter.CTk()
    app = GUI(root)
    root.mainloop()
    exit(0)