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
            degree_programs.append(degree.text)
    return degree_programs
        

def get_curric(degree_program):
    req = requests.get("https://bulletin.temple.edu/undergraduate/science-technology/" + '-'.join(degree_program.lower().split()) + "/#requirementstext")
    soup=BeautifulSoup(req.content,'html.parser')
    requirements_html = soup.find('div',id='requirementstextcontainer')
    courses_html = requirements_html.find_all('a',class_='bubblelink code')
    curric = []
    for c in courses_html:
        course = c.text
        curric.append(str(course))
    return curric
   
        



#print(get_curric("Computer Science BS"))
print(get_degree_programs())
