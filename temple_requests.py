import requests
from bs4 import BeautifulSoup

def get_curric(course_of_study):
    req = requests.get("https://bulletin.temple.edu/undergraduate/science-technology/" + '-'.join(course_of_study.lower().split()) + "/#requirementstext")
    soup=BeautifulSoup(req.content,'html.parser')
    requirements_html = soup.find('div',id='requirementstextcontainer')
    courses_html = requirements_html.find_all('a',class_='bubblelink code')
    curric = []
    for c in courses_html:
        course = c.text
        curric.append(str(course))
    return curric
   
        



print(get_curric("Computer Science BS"))
