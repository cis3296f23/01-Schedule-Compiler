from flask import Flask, request
from temple_bulletin_api import get_degr_progs, get_curric
from tuportal_api import get_param_data_codes
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
    curric_url = request.args.get("curric_url")
    if curric_url:
        return get_curric(urllib.parse.unquote(curric_url))
    else:
        return "Link not valid or no link passed."

@app.route("/param_data_codes")
def param_data_codes():
    param_type = request.args.get("param_type")
    if param_type:
        return get_param_data_codes(param_type)
    else:
        return "Parameter type not valid or no parameter passed."

if __name__=="__main__":
    app.run(debug=True)