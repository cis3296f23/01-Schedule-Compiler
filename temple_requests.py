import requests
from bs4 import BeautifulSoup
import re
from algo import Schedule

PAGE_MAX_SIZE = 50
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

def get_degr_urls_and_abbrvs(degrs_html_str:str,col_num:int,start:int):
    """
    Retrieves the url for a specific degree program and the abbreviation of the level (i.e. MS or BA)
    @param degrs_html_str : str with a portion of html to parse
    @param col_num : column number to indicate section of html to look at (1:undergraduate, 2:graduate, 3:professional)
    @param start : current index in degrs_html_str
    @return : array of tuples in the form (degr_url, abbrv) and i if there is at least one link and abbreviation, otherwise an empty array and the parameter start are returned
    """
    urls_and_abbrvs_arr = []
    href_ind = degrs_html_str.find('href',start)
    abbrv_ind = degrs_html_str.find('>',href_ind)
    i=0
    #if there is a link to a degree program (which is in the href tag) in the current column 
    while href_ind>0 and href_ind<degrs_html_str.find('column'+str(col_num+1)):
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
        urls_and_abbrvs_arr.append((degr_url, abbrv))
        href_ind = degrs_html_str.find('href',i)
        if href_ind!=-1:
            abbrv_ind = degrs_html_str.find('>',href_ind)
    #return blank strs if there is no link/degree program for the current column indicated by col_num (while loop never executed)
    if not i:
        return [],start
    return urls_and_abbrvs_arr,i

def get_degr_progs()->dict:
    """
    Retrieves all degree programs at Temple University from its Academic Bulletin
    @return : a dictionary of degree program strings mapped to their corresponding links, otherwise None on error
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
                    urls_and_abbrvs_arr, next_col_str_search_start_ind = get_degr_urls_and_abbrvs(degrs_html_str, i,degrs_html_str.find('column' + str(i),next_col_str_search_start_ind))
                    for url_and_abbrv in urls_and_abbrvs_arr:
                        abbrv = url_and_abbrv[1]
                        if abbrv and 'not currently' not in abbrv:
                            degr_program_to_url[subj+' '+abbrv]=url_and_abbrv[0]
            elif not html.text.isspace():
                subj = get_subj(degrs_html_str,'column0',0,9)
                next_col_str_search_start_ind = 0
                for i in range(1,4):
                    urls_and_abbrvs_arr, next_col_str_search_start_ind = get_degr_urls_and_abbrvs(degrs_html_str, i,degrs_html_str.find('column' + str(i),next_col_str_search_start_ind))
                    for url_and_abbrv in urls_and_abbrvs_arr:
                        abbrv = url_and_abbrv[1]
                        if abbrv and 'not currently' not in abbrv:
                            degr_program_to_url[subj+' '+abbrv]=url_and_abbrv[0]
        return degr_program_to_url
    except Exception as e:
        return {f"Try connecting to the internet and restarting the application. \nResulting error(s): {e}":""}

def get_curric(degr_prog_url:str)->list[str]:
    """
    Retrieves the curriculum for the specified degree program
    @param degr_prog_url : the portion of the url for the specific degree program
    @return : list of tuples with format (SUBJ ####, Course_Name) for courses in the curriculum in the requirements section of the degree program link specified by degr_prog_url, otherwise empty array on failure or if Temple is not accepting applications for the curriculum
    """
    try:
        req = requests.get("https://bulletin.temple.edu/" + degr_prog_url + "#requirementstext")
        soup=BeautifulSoup(req.content,'html.parser')
        requirements_html = soup.find('div',id='requirementstextcontainer')
        if requirements_html==None:
            requirements_html = soup.find('div', id='programrequirementstextcontainer')
            if requirements_html == None:
                return []
        courses_html = requirements_html.find_all('tr',class_=re.compile('(^.*even*$|^.*odd.*$)'))
        curric = []
        for c in courses_html:
            subj_and_num_html = c.find('a',class_='bubblelink code')
            #checks to make sure the html has course info, and if it does, it looks for the course subject, number and name
            if subj_and_num_html:
                subj_and_num = subj_and_num_html.text
                td_htmls = c.find_all('td')
                course_name = td_htmls[1].text
                if (subj_and_num,course_name) not in curric:
                    curric.append([subj_and_num,course_name])
        return curric
    except Exception as e:
        return [f"Try connecting to the internet and restarting the application. \nResulting error(s): {e}"]

def get_param_data_codes(endpoint:str)->dict:
    """
    Retrieves the code used to specify the certain parameter data in url queries such as semester and campus
    Credit: Neil Conley (Github: gummyfrog)
    @param endpoint: str representing endpoint for specific parameter data (i.e. "getTerms" or "get_campus")
    @return : dictionary mapping data codes to corresponding potential parameter data on success, otherwise None on error
    """
    PAGINATION_OPTS = {
     "offset": "1",
     "max": "10",
    }
    try:
        response = requests.get("https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/classSearch/"+endpoint, PAGINATION_OPTS)
        param_data_to_code = dict()
        data=response.json()
        for descrip_and_code in data:
            if endpoint=="getTerms" and "Orientation" in descrip_and_code['description']:
                continue
            param_data_to_code[descrip_and_code['description']]=descrip_and_code['code']
        return param_data_to_code
    except Exception as e:
        return {f"Try connecting to the internet and restarting the application. \nResulting error(s): {e}":""}

#can retrieve other info such as "Would take again" and difficulty later on if it helps
def get_rmp_data(prof:str):
    """
    Retrieves information from ratemyprofessors.com related to the specified professor's ratings.
    
    @param prof : professor to retrieve information about on ratemyprofessors.com
    @return : array of non-zero rating and non-zero rating amount on success, array of 0.0 and 0.0 on failure or if no entry can be found for the professor
    """
    try:
        prof_search_req = requests.get("https://www.ratemyprofessors.com/search/professors/999?q="+'%20'.join(prof.split()))
    except:
        print("Ignore: Professor rating data not available")
        return [0.0, 0.0]
    
    #credit to Nobelz in https://github.com/Nobelz/RateMyProfessorAPI for retrieval of RMP professor ids
    prof_ids = re.findall(r'"legacyId":(\d+)', prof_search_req.text)
    
    #loops through the professor ids found based on search by professor name
    for id in prof_ids:
        try:
            prof_rating_req = requests.get("https://www.ratemyprofessors.com/professor/" + id)
            soup = BeautifulSoup(prof_rating_req.content, 'html.parser')
            
            #extract the professor's name from the page to verify the match
            prof_name_tag = soup.find("span", class_="NameTitle__Name-dowf0z-0")
            if prof_name_tag:
                prof_name = prof_name_tag.get_text().strip().lower()
                input_name = prof.strip().lower()
                
                #check if input name matches the professor's name using regex or substring
                if not (re.search(input_name, prof_name) or input_name in prof_name):
                    continue
            
            #rating retrieval
            rating_html = str(soup.find("div", re.compile("^RatingValue__Numerator")))
            rating = ''
            i = rating_html.rfind('<') - 1
            while rating_html[i] != '>':
                rating += rating_html[i]
                i -= 1
            rating = float(rating[::-1])
            
            #retrieval of number of ratings
            num_ratings = ''
            num_reviews_html = str(soup.find("div", re.compile("^RatingValue__NumRatings")))
            i = num_reviews_html.rfind('\">') + 2
            while num_reviews_html[i] != '<':
                num_ratings += num_reviews_html[i]
                i += 1
            
            #if there are no ratings, continue to the next professor ID
            if rating == 0.0 or float(num_ratings) == 0.0:
                continue
            
            return [rating, float(num_ratings)]
        except Exception as e:
            print(f"Ignore: Professor rating not found for id {id}")
    
    return [0.0, 0.0]

def get_weighted_rating(sect_info):
    """
    Calculates weighted rating for professor based on data in sect_info to help sort the sections for a course
    @param sect_info : one course section's data
    """
    return sect_info['profRating'],sect_info['numReviews']

def get_authenticated_session(search_args:dict):
    """
    Returns an authenticated session for searching in TUPortal's class scheduling service and the updated result arguments
    @param search_args
    """
    session = requests.Session()
    # extra stuff for the results
    results_opts = {
        "pageOffset": 0,
        "pageMaxSize": PAGE_MAX_SIZE,
        "sortColumn": "subjectDescription",
        "sortDirection": "asc",
    }
    results_args = dict()
    results_args.update(search_args)
    results_args.update(results_opts)
    try:
        # Establish session
        session.post("https://prd-xereg.temple.edu/StudentRegistrationSsb/")
        # Select a term
        session.post("https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/term/search?mode=search", search_args)
    except Exception as e:
        return f"Try connecting to the internet and restarting the application. \nResulting error(s): {e}", None
    return session, results_args

def fetch_course_data(session, search_args, results_args)->dict:
    """
    Retrieves course data from TUPortal scheduling service
    @param session : reference to authenticated session
    @param search_args
    @param results_args : 
    @return data for retrieved sections of courses
    """
    # Start class search for the chosen term and current page offset
    session.post("https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/classSearch/get_subject?offset=" + str(int(results_args["pageOffset"]/PAGE_MAX_SIZE)+1) + "&max="+str(PAGE_MAX_SIZE), search_args)
    # Clear old results, if any
    session.post("https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/classSearch/resetDataForm")
    # Execute search
    response = session.post("https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/searchResults/searchResults?startDatepicker=&endDatepicker=", results_args)
    data = response.json()
    data["ztcEncodedImage"] = ""
    return data

def get_courses_from_keyword_search(term_code:str,keywords:str)->set:
    """
    Returns a set of courses (in the format: SUBJ #### Title) available during the specified term that are returned from the keywords search
    @param term_code : code for semester desired (i.e. Spring 2024)
    @param keywords : string to search for
    """
    courses = set()
    SEARCH_REQ = {"txt_keywordall":keywords,"term": term_code, "txt_term": term_code}
    session, results_args = get_authenticated_session(SEARCH_REQ)
    if type(session)==str:
        return [(session,"")]
    moreResults=True
    while moreResults:
        try:
            data = fetch_course_data(session,SEARCH_REQ,results_args)
            if data['totalCount']>results_args['pageOffset']+PAGE_MAX_SIZE:
                results_args['pageOffset']+=PAGE_MAX_SIZE
            else:
                moreResults=False
            if data['totalCount']:
                for section in data['data']:
                    courses.add((section['subject'] + ' ' + section['courseNumber'],section['courseTitle']))
            else:
                return [("There are no courses that have the keyword(s) you entered.","")]
        except Exception as e:
            return [(f"Try connecting to the internet and restarting the application. \nResulting error(s): {e}","")]
    return courses

def get_course_sections_info(course_info : dict, term:str, term_code:str,subj:str="",course_num:str="",attr="", campus_code = "MN", prof_rating_cache = {}):
    """
    Retrieves info on the sections available during the specified term for the specified class
    @param course_info : dictionary to store the necessary section information in for each course in the format {"Fall 2023":{"Subj_course_num1":[{},{}], "Subj_course_num2":[{}]} ,"Spring 2024":{"Subj_course_num3":[{},{}], "Subj_course_num4":[{}]}}
    @param term : semester desired (i.e. Spring 2024)
    @param term_code : number representing the semester
    @param subject : abbreviation representing the subject of the course
    @param course_num : number of the course
    @param attr : 2 character string attribute of the course (i.e. GU for Gened United States or GY for Intellectual Heritage I)
    @param prof_rating_cache : stores previously retrieved professor ratings for the session to reduce the number of requests made
    @return : empty string on success, error message on failure
    Credit: https://github.com/gummyfrog/TempleBulletinBot
    """
    #if course info for the desired semester is already course_info, return
    if term in course_info and campus_code in course_info[term] and (subj + ' ' + course_num in course_info[term][campus_code] or attr in course_info[term][campus_code]):
        return
    if term not in course_info:
        course_info[term]=dict()
    if campus_code not in course_info[term]:
        course_info[term][campus_code]=dict()
    # term and txt_term need to be the same
    SEARCH_REQ = {
        "term": term_code,
        "txt_term": term_code,
        "txt_subject": subj,
        "txt_courseNumber": course_num,
        "txt_attribute": attr,
        "txt_campus": campus_code
    }
    session, results_args = get_authenticated_session(SEARCH_REQ)
    moreResults=True
    while moreResults:
        try:
            data = fetch_course_data(session,SEARCH_REQ,results_args)
            if data['totalCount']>results_args['pageOffset']+PAGE_MAX_SIZE:
                results_args['pageOffset']+=PAGE_MAX_SIZE
            else:
                moreResults=False
            if data['totalCount']:
                for section in data['data']:
                    if section['faculty']:
                        professor = section['faculty'][0]['displayName']
                        rmp_info = prof_rating_cache.get(professor)
                        if not rmp_info:
                            rmp_info = get_rmp_data(professor)
                            prof_rating_cache[professor]=rmp_info
                    sched = Schedule()
                    days_of_the_week = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
                    for meeting_type in section['meetingsFaculty']:
                        meet_time_info = meeting_type['meetingTime']
                        for day in days_of_the_week:
                            if meet_time_info[day]:
                                sched.add_timeslot(day,int(meet_time_info['beginTime']),int(meet_time_info['endTime']),meet_time_info['meetingTypeDescription'])
                    #partOfTerm included in case can schedule two courses with the same meeting times but in different parts of the semester
                    sect_info = {'name':section['subject'] + ' ' + section['courseNumber'],'term':section['term'],'CRN':section['courseReferenceNumber'],
                                'partOfTerm':section['partOfTerm'],'seatsAvailable':section['seatsAvailable'],'maxEnrollment':section['maximumEnrollment'],
                                'creditHours':section['creditHourLow'] if section['creditHourLow'] else section['creditHourHigh'], 
                                'professor':professor,'profRating':rmp_info[0],'numReviews':rmp_info[1],'schedule':sched}
                    course = section['subject'] + ' ' + section['courseNumber'] if not attr else attr
                    course_sections = course_info[term][campus_code].get(course)
                    if not course_sections:
                        course_info[term][campus_code][course] = [sect_info]
                    else:
                        course_sections.append(sect_info)
            else:
                return 'Invalid course or course not available'
        except Exception as e:
            return f"Try connecting to the internet and restarting the application. \nResulting error(s): {e}"
    if subj: #if subj and course_num given
        course_info[term][campus_code][subj + ' ' + course_num].sort(reverse=True,key=get_weighted_rating)
    else:
        course_info[term][campus_code][attr].sort(reverse=True,key=get_weighted_rating)
    return ''
        
"""degr_progs= get_degr_progs()
for dgpg in degr_progs:
    get_curric(degr_progs[dgpg])"""
#print(get_param_data_codes('getTerms'))
#print(get_param_data_codes('get_campus'))
"""course_info = dict()
get_course_sections_info(course_info,"2023 Fall", "202336",attr="GA")
print(len(course_info["2023 Fall"]["MN"]["GA"]))
get_course_sections_info(course_info,"2024 Spring", "202403","CIS","2168",'')
print(course_info)"""
#print(get_rmp_data("Sarah Stapleton"))
#print(get_courses_from_keyword_search("202436","Data Structures"))