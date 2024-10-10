from flask import Flask
from temple_bulletin_api import get_degr_progs


app = Flask(__name__)


@app.route("/")
def index():
    return "Welcome to the Schedule Compiler"

#rate limit Temple endpoints

@app.route("/degree_programs")
def degree_programs():
    return get_degr_progs()

if __name__=="__main__":
    app.run(debug=True)