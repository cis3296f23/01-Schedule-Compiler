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
- Use this github repository
- Specify what branch to use for a more stable release or for cutting edge development.  
- Use any IDE that works with Python
- Set up virtual environment once by running "py -3 -m venv .venv"
- Run virtual environment by typing and entering ".venv/scripts/activate" (Do this every time you enter the project)
- Run "pip install -r requirements.txt"
- Run gui.py
- User interface should show up with title "Schedule Compiler" and options for preferences in schedule creation
