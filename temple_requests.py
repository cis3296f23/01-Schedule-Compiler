import requests
from bs4 import BeautifulSoup

def get_degree_programs():
    #first try to create dictionary of links to degree programs based on html that leads to links (should find subject and level too)
    req = requests.get("https://bulletin.temple.edu/academic-programs/")
    soup = BeautifulSoup(req.content,'html.parser')
    degree_programs_html = soup.find('tbody', class_='fixedTH',id='degree_body')
    i = 0
    degree_programs = []
    for degree in degree_programs_html:
        if not degree.text.isspace() and '/' not in degree.text:
            #can later split by level of program
            degree_programs.append(degree.text)
    return degree_programs
        
#degree_program will need to be formatted specifically for certain degree programs, but for most it can be assumed to just join the phrases with a '-'
def get_curric(degree_program):
    #create dictionary to match up level and school to each degree program
    #if first letter of level is 'A' or 'B' then level = undergraduate 
    level = 'undergraduate/'
    school = 'science-technology/'
    req = requests.get("https://bulletin.temple.edu/" + level +school+ '-'.join(degree_program.lower().split()) + "/#requirementstext")
    soup=BeautifulSoup(req.content,'html.parser')
    requirements_html = soup.find('div',id='requirementstextcontainer')
    courses_html = requirements_html.find_all('a',class_='bubblelink code')
    curric = []
    for c in courses_html:
        #can later account for the "\xa0" in the middle of each, but printing each element produces the desired format
        curric.append(c.text)
    return curric

def get_term_codes():
    PAGINATION_OPTS = {
     "offset": "1",
     "max": "10",
    }
    response = requests.get("https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/classSearch/getTerms", PAGINATION_OPTS)
    return(response.json())

def get_course_sections_info(term_code,subject,course_num,attr=''):
    session = requests.Session()
    # term and txt_term need to be the same
    SEARCH_REQ = {
        "term": term_code,
        "txt_term": term_code,
        "txt_subject": subject,
        "txt_courseNumber": course_num,
        "txt_attribute": attr
    }
    # extra stuff for the results
    RESULTS_OPTS = {
        "pageOffset": 0,
        "pageMaxSize": 10,
        "sortColumn": "subjectDescription",
        "sortDirection": "asc",
    }

    RESULTS_ARGS = dict()
    RESULTS_ARGS.update(SEARCH_REQ)
    RESULTS_ARGS.update(RESULTS_OPTS)

    # Establish session
    session.post("https://prd-xereg.temple.edu/StudentRegistrationSsb/")
    # Select a term
    session.post("https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/term/search?mode=search", SEARCH_REQ)
    # Start subject search for the chosen term
    session.post("https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/classSearch/get_subject?offset=1&max=10", SEARCH_REQ)
    # Clear old results, if any
    session.post("https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/classSearch/resetDataForm")
    # Execute search
    response = session.post("https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/searchResults/searchResults?startDatepicker=&endDatepicker=", RESULTS_ARGS)

    data = response.json()
    data["ztcEncodedImage"] = ""
    return data
    
    

   
#print(get_degree_programs())
#print(get_curric("Computer Science BS"))
#print(get_term_codes())
#print(get_course_sections_info("202336","EES","2021",''))