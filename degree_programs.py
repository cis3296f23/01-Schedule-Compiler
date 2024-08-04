import re
import requests
from bs4 import BeautifulSoup

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
