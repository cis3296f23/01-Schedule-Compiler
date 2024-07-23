from config import PAGE_MAX_SIZE
from temple_api import get_authenticated_session, fetch_course_data
from professor_ratings import get_rmp_data, get_weighted_rating
from classes.Schedule import Schedule


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
