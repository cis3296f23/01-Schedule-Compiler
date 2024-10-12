from flask import Flask, request
from temple_bulletin_api import get_degr_progs, get_curric
from tuportal_api import get_param_data_codes, get_courses_from_keyword_search
import urllib.parse


app = Flask(__name__)


@app.route("/")
def index():
    return "Welcome to the Schedule Compiler"

#rate limit Temple endpoints

@app.route("/degree_programs")
def degree_programs():
    """
    Returns a dictionary of degree program names mapped to subdomain urls
    """
    return get_degr_progs()

@app.route("/curriculum")
def curric():
    """
    Fetches courses in the curriculum for a specific degree program

    curric_url : url for the desired curriculum
    """
    curric_url = request.args.get("curric_url")
    if curric_url:
        return get_curric(urllib.parse.unquote(curric_url))
    else:
        return "Link not valid or no link passed."

@app.route("/param_data_codes")
def param_data_codes():
    """
    Fetches the codes corresponding to data of a certain type (e.g. semester to number code or campus to letter code)

    param_type : type of parameter (either getTerms or get_campus)
    """
    param_type = request.args.get("param_type")
    if param_type:
        return get_param_data_codes(param_type)
    else:
        return "Parameter type not valid or no parameter passed."
    
@app.route("/keyword_search_courses")
def keyword_search_courses():
    """
    Calls the TUPortal API function to search courses by keyword and returns the resulting dict

    term : semester to look for available courses
    keywords
    """
    term = request.args.get("term")
    keywords = request.args.get("keywords")
    if term and keywords:
        return list(get_courses_from_keyword_search(term, keywords))
    else:
        return "Term and/or keyword not provided or invalid."

if __name__=="__main__":
    app.run(debug=True)