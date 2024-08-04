import requests
from config import PAGE_MAX_SIZE

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
