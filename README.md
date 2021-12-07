# huds-green

To setup debug mode:
 1. CD into project folder
 2. Run `chmod +x bin/server-debug.sh`
 3. To launch Flask in debug mode, just run `bin/server-debug.sh`
 4. Packages listed in requirements.txt must be installed.

To run the program locally:
 1. CD into project folder   
 2. Run 'flask run'
 3. Packages listed in requirements.txt must be installed.


To run the program remotely:
 1. Visit https://huds-green.herokuapp.com/.

static:

templates: This folder contains all of our HTML pages.

app.py: This file defines the "POST" and "GET" method for all pages. It also contains the functions that query the HUDS database for the daily meny using the HUIT Dining API and generate meal recommendations.

bin, venv:
