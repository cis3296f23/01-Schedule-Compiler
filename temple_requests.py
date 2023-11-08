import requests
from bs4 import BeautifulSoup

def get_degree_programs():
    req = requests.get("https://bulletin.temple.edu/academic-programs/")
    soup = BeautifulSoup(req.content,'html.parser')
    degree_programs_html = soup.find('tbody', class_='fixedTH',id='degree_body')
    i = 0
    degree_programs = []
    for degree in degree_programs_html:
        if not degree.text.isspace():
            #can later split by level of program (the abbreviations that follow after some amount of spaces in each element)
            degree_programs.append(degree.text)
    return degree_programs
        

def get_curric(degree_program):
    req = requests.get("https://bulletin.temple.edu/undergraduate/science-technology/" + '-'.join(degree_program.lower().split()) + "/#requirementstext")
    soup=BeautifulSoup(req.content,'html.parser')
    requirements_html = soup.find('div',id='requirementstextcontainer')
    courses_html = requirements_html.find_all('a',class_='bubblelink code')
    curric = []
    for c in courses_html:
        #can later account for the "\xa0" in the middle of each, but printing each element produces the desired format
        curric.append(c.text)
    return curric
   
print(get_degree_programs())
print(get_curric("Computer Science BS"))