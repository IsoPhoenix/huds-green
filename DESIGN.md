HOW WE SET UP THE PROGRAM: The program was set up in the VSCode IDE. We used Github to collaborate. The program is reachable through HerokuApp.

HOW WE STYLED THE PROGRAM: We primarily relied on bootstrap functionality to build out our website.


HOW WE GENERATE THE HOME PAGE:


HOW WE GENERATE RECOMMENDED MEALS: 
The Decarbonize My Meal page uses a form to collect user preferences, which are then input into a Python script. Specifically, we call the daily HUDS menu using the HUIT Dining API, which creates a dataframe of today's menu items. We specifically use the variable Serve_Date in tandem with the Python package datetime to query for today's menu only. With user input, we are also able to further filter down the data by dining location.

The Decarbonize My Meal generates 3 types of options using 3 functions: vegetarian(), vegan(), and chicken():

The vegetarian function filters down the dataframe to menu items that are high in protein (i.e. more than 5g/serving) and are vegetarian (Recipe_Web_Code contains VGT). Then, it sorts the dataframe in descending order. It takes the head() of that dataframe, where the number of rows is determined by the total protein given by 1 serving of each food. We calculate sufficient based on user input, weight and number of meals in a day, which is then matched to the Recommneded Daily Allowance of protein. In the HTML, we choose to display calorie count in addition to serving size and protein amount because we thought it was important for users to gauge what else they should be eating in addition to protein. We chose to focus on protein because protein is both the main concern for people who are considering vegetarianism and the most carbon-intensive source of food.

The vegan and chicken functions function similarly, but they filter down the menu dataframe using different values (Recipe_Web_Code contains VGT for vegan() and all VGT, chicken, and fish options for chicken()).

Given what the user identifies as their dietary preference, we call the 3 functions accordingly.

*Note: The Adams dining location does not generate output because its data is labeled differently than all the other dining locations (i.e. Adams does not label its lunch menu items as "Lunch"). Because all other dining locations are consistent, we chose to abide by that consistency and leave the error with Adams.