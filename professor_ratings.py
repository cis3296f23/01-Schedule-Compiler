import requests
import re
from bs4 import BeautifulSoup

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
