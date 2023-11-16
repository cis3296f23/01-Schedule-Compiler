import requests
from bs4 import BeautifulSoup
import re

def get_subj(degrs_html_str:str,str_to_search:str,start:int,offset_to_subj:int)->str:
    """
    Retrieves the subject of the degree program from the given html
    @param degrs_html : html with degree program information
    @param str_to_search : unique part of the html to search for to bring index i closer to subject text
    @param start : starting index of degrs_html_str for find() method to start looking for str_to_search
    @param offset_to_subject : offset needed to get i to be the index of the first character of subject
    @return subj : str representing a subject for a degree program (i.e. Biology)
    """
    subj = ''
    i = degrs_html_str.find(str_to_search,start)+offset_to_subj
    while degrs_html_str[i]!='<':
        subj+=degrs_html_str[i]
        i+=1
    return subj

def get_degr_url_and_abbrv(degrs_html_str:str,col_num:int,start:int):
    """
    Retrieves the url for a specific degree program and the abbreviation of the level (i.e. MS or BA)
    @param degrs_html_str : str with a portion of html to parse
    @param col_num : column number to indicate section of html to look at (1:undergraduate, 2:graduate, 3:professional)
    @param start : current index in degrs_html_str
    @return : degr_url, abbrv, i if there is a link and abbreviation, otherwise two empty strings and the parameter start
    """
    href_ind = degrs_html_str.find('href',start)
    abbrv_ind = degrs_html_str.find('>',href_ind)
    #if there is a link to a degree program (which is in the href tag) in the current column 
    if href_ind>0 and href_ind<degrs_html_str.find('column'+str(col_num+1)):
        i=0
        degr_url = ''
        abbrv = ''
        i=href_ind+6
        while degrs_html_str[i]!='\"':
            degr_url+=degrs_html_str[i]
            i+=1
        #next move i to where the abbrev is
        i=abbrv_ind+1
        while degrs_html_str[i]!='<':
            abbrv+=degrs_html_str[i]
            i+=1
        #i is returned to use in making it faster to find the next starting index with find() (where 'column#' is)
        return degr_url, abbrv,i
    #return blank strs if there is no link/degree program for the current column indicated by col_num
    return '', '',start

def get_degr_progs()->dict:
    """
    Retrieves all degree programs at Temple University from its Academic Bulletin
    @return : a dictionary of degree program strings mapped to their corresponding links, otherwise an empty dictionary
    """
    try: 
        degr_program_to_url = dict()
        req = requests.get("https://bulletin.temple.edu/academic-programs/")
        soup = BeautifulSoup(req.content,'html.parser')
        degr_programs_htmls = soup.find('tbody', class_='fixedTH',id='degree_body')
        for html in degr_programs_htmls:
            degrs_html_str = str(html)
            #special case for first row where the style is being set (html has extra stuff)
            if 'style' in degrs_html_str:
                subj = get_subj(degrs_html_str,'>',degrs_html_str.find('column0'),1)
                next_col_str_search_start_ind = 0
                for i in range(1,4):
                    degr_url, abbrv, next_col_str_search_start_ind = get_degr_url_and_abbrv(degrs_html_str, i,degrs_html_str.find('column' + str(i),next_col_str_search_start_ind))
                    if abbrv:
                        #modify to include abbrv with subject
                        degr_program_to_url[subj+' '+abbrv]=degr_url
            elif not html.text.isspace():
                subj = get_subj(degrs_html_str,'column0',0,9)
                next_col_str_search_start_ind = 0
                for i in range(1,4):
                    degr_url, abbrv, next_col_str_search_start_ind = get_degr_url_and_abbrv(degrs_html_str, i,degrs_html_str.find('column' + str(i),next_col_str_search_start_ind))
                    if abbrv and 'not currently' not in abbrv:
                        #modify to include abbrv with subject
                        degr_program_to_url[subj+' '+abbrv]=degr_url
        return degr_program_to_url
    except Exception as e:
        return dict()
    #return empty dict if error occurred
    return dict()

#degree_program will need to be formatted specifically for certain degree programs, but for most it can be assumed to just join the phrases with a '-'
def get_curric(degr_prog_url:str)->list[str]:
    """
    Retrieves the curriculum for the specified degree program
    @param degr_prog_url : the portion of the url for the specific degree program
    @return : list of courses in the curriculum in the requirements section of the degree program link specified by degr_prog_url, otherwise empty array on failure or if Temple is not accepting applications
    """
    try:
        req = requests.get("https://bulletin.temple.edu/" + degr_prog_url + "#requirementstext")
        soup=BeautifulSoup(req.content,'html.parser')
        requirements_html = soup.find('div',id='requirementstextcontainer')
        if requirements_html==None:
            requirements_html = soup.find('div', id='programrequirementstextcontainer')
            if requirements_html == None:
                return []
        courses_html = requirements_html.find_all('a',class_='bubblelink code')
        curric = []
        for c in courses_html:
            #can later account for the "\xa0" in the middle of each, but printing each element produces the desired format
            curric.append(c.text)
        return curric
    except:
        return []

def get_term_codes()->dict:
    """
    Retrieves the numbers used to specify the semester in url queries
    Credit: Neil Conley (Github: gummyfrog)
    @return : dictionary mapping str term codes to str semester
    """
    PAGINATION_OPTS = {
     "offset": "1",
     "max": "10",
    }
    response = requests.get("https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/classSearch/getTerms", PAGINATION_OPTS)
    return(response.json())

def get_course_sections_info(term_code:str,subj:str,course_num:str,attr='')->dict:
    """
    Retrieves info on the sections available during the specified term for the specified class
    @param term_code : number representing the semester
    @param subject : abbreviation representing the subject of the course
    @param course_num : number of the course
    @param attr : attribute of the course (i.e. GU for Gened United States or GY for Intellectual Heritage I)
    @return : dictionary of course section information that students can see when clicking on a course section for registration or planning
    Credit: https://github.com/gummyfrog/TempleBulletinBot
    """
    session = requests.Session()
    # term and txt_term need to be the same
    SEARCH_REQ = {
        "term": term_code,
        "txt_term": term_code,
        "txt_subject": subj,
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

#can retrieve other info such as "Would take again" and difficulty later on if it helps
def get_rmp_data(prof:str):
    """
    Retrieves information from ratemyprofessors.com related to the specified professor's ratings
    @param prof : professor to retrieve information about on ratemyprofessors.com
    @return : array of non-zero rating and non-zero rating amount on success, array of None and 0 on failure
    """
    prof_search_req = requests.get("https://www.ratemyprofessors.com/search/professors/999?q="+'%20'.join(prof.split()))
    #credit to Nobelz in https://github.com/Nobelz/RateMyProfessorAPI for retrieval of RMP professor ids
    prof_ids = re.findall(r'"legacyId":(\d+)', prof_search_req.text)
    #loops through the professor ids found based on search by professsor name
    for id in prof_ids:
        try:
            prof_rating_req = requests.get("https://www.ratemyprofessors.com/professor/" + id)
            soup=BeautifulSoup(prof_rating_req.content,'html.parser')
            #rating retrieval
            rating_html = str(soup.find("div",re.compile("^RatingValue__Numerator")))
            rating = ''
            i = rating_html.rfind('<')-1
            while rating_html[i]!='>':
                rating+=rating_html[i]
                i-=1
            rating = rating[::-1]
            #retrieval of number of ratings
            num_ratings=''
            num_reviews_html = str(soup.find("div",re.compile("^RatingValue__NumRatings")))
            i=num_reviews_html.rfind('\">')+2
            while num_reviews_html[i]!='<':
                num_ratings+=num_reviews_html[i]
                i+=1
            return [rating,num_ratings]
        except:
            return [None,0]
        
"""degr_progs= get_degr_progs()
for dgpg in degr_progs:
    get_curric(degr_progs[dgpg])"""
#print(get_term_codes())
#print(get_course_sections_info("202336","EES","2021",''))
#print(get_rmp_rating("Sarah Stapleton"))