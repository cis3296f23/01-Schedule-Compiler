import requests
from config import PAGE_MAX_SIZE
from professor_ratings import get_rmp_data, get_weighted_rating
from classes.Schedule import Schedule

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
