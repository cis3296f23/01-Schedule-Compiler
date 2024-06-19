# Schedule Compiler
This is a desktop application for Temple students which helps create a schedule for their next semester based on their course of study, classes they have taken and need to take, professor ratings, and user selected prioritization of classes and days they would like to attend class.

# How to run

## For Windows
1. Click on Releases to get the latest release
2. Click on schedule_compiler.exe to download the executable
3. Move the file whereever you would like and double click to run

## For Mac and Linux
1. Download the tar.gz file
2. Unzip the file and navigate to the project directory
3. Set up virtual environment once by running "py -3 -m venv .venv"
4. Run virtual environment by typing and entering ".venv/scripts/activate" (Do this every time you enter the project)
5. Run "pip install -r requirements.txt"
6. Run "pyinstaller --onefile schedule_compiler.py"
7. When the command is finished, run "./dist/schedule_compiler.exe"

# How to contribute
Follow this project board to know the latest status of the project in the project board. Submit a PR with working code.

### How to build

- Clone the repository in your desired IDE that works with Python
- Set up the virtual environment (done only once):
    - For Windows, run "py -3 -m venv .venv"
    - For Linux, run "python3 -m venv .venv"
-Run the virtual environment (done every time you open up the project):
    - For Windows, run ".venv/scripts/activate"
    - For Linux, run "source .venv/bin/activate"
- Run "pip install -r requirements.txt"
- In Linux, run "sudo apt-get install python3-tk"
- Run schedule_compiler.py
- User interface should show up with title "Schedule Compiler" and options for preferences in schedule creation
