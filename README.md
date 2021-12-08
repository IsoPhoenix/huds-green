# huds-green

## Accessing and using the app

Welcome to HUDS Green! HUDS Green lists carbon-friendly options for the day and suggests personalized carbon-friendly meals given your dietary needs.

To run the app, simply visit https://huds-green.herokuapp.com/.

On the Home page, you can select your dining location through the dropdown menu, and the app will update with the HUDS lunch and dinner menus for your location. Use the tabs to choose between lunch and dinner menus. Only the most carbon-friendly menu options are displayed by default, but you can choose to view the entire menu by hitting the `All Options` button.

To receive a personalized meal recommendation with carbon-friendly options based on your dietary preferences and weight, visit the `Decarbonize My Meal` page from the navbar. Fill out the form with your preferences to receive a table of recommendations. Information about serving sizes and total calories is included to help you track your calories if needed!

Finally, visit the `About` page to learn more about carbon-friendly eating, the app itself, and the developers!

## Running the app locally

- Clone the GitHub repo to your computer. You can use `git clone https://github.com/IsoPhoenix/huds-green.git`. Alternatively, if you are using the zip file from Gradescope, you can unzip the file, `cd` into the project directory, and skip straight to the `source venv/bin/activate` step.
- HUDS Green is a Flask webapp. We recommend using a Python virtual environment for package management if you plan on running/developing the app locally. To set up a virtual environment, `cd` into your project folder and run `python -m venv venv/`. If you get a `No module named venv` error, try `python3 -m venv venv/`.
- Activate the virtual environment by running `source venv/bin/activate`.
- While in your virtual environment, use `pip install <MODULE-NAME-HERE>` to install all the necessary packages. This includes `Flask`, `pandas`, `requests`, `gunicorn`, and `DateTime`. You can find a comprehensive list of dependencies in `requirements.txt`.
- To run the app, use `flask run`.
- To run the app in development mode, first run `chmod +x bin/server-debug.sh`. Then, you can run `bin/server-debug.sh` inside the project folder, which acts as a shortcut to run the webapp in development mode.

## Files/folders explained

- `app.py`: Contains the server backend, including important Flask logic, API calls, and carbon-friendly calculations.
- `/templates`: Contains all HTML template files.
- `/static`: Contains static files like images and CSS styling.
- `bin/server-debug.sh`: A short shell script that allows for easy launching in development mode.
- `Procfile` and `requirements.txt`: Files used by Heroku to host the webapp and manage dependencies.
