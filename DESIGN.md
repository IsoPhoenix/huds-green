# Design of HUDS Green

## Overview of high-level structure and design process

We decided to develop HUDS Green as a Flask webapp serving a traditional HTML/CSS/Js frontend (styled with Bootstrap) because that was the tech stack with which we were most familiar from CS50. Earlier on, we considered using a React frontend but decided against it since we felt that the UI was not complicated/extensive enough to necessitate a more robust frontend framework.

In order to obtain HUDS dining information, the webapp calls the [HUIT Dining Services API](https://portal.apis.huit.harvard.edu/dining-overview) for information about dining locations, menu items, and recipes. Alternatively, we could have used the [CS50 Dining API](https://cs50.readthedocs.io/api/dining/), which would have provided data in a more polished format, but that API is outdated (does not contain up-to-date dining info), so we decided to use the HUIT API instead and perform a little more data processing on the backend.

In particular, our app makes extensive use of `pandas`, which is a popular python library for data manipulation via use of `dataframe` objects. We used `pandas` to format, sort, and filter the information received from the HUIT API. During the development process, we also used Deepnote, an online IDE for python scripting, to test our API calls and ensure data was properly formatted.

Finally, the app is deployed on Herokuapp to allow easy access through the web browser, and it is both mobile and desktop compatible.

## How we styled the program:

The website styling is handled by Bootstrap (with default styling). In future iterations of the app, a customized color/styling theme could potentially be created. However, this would require either utilizing manual styling in lieu of Bootstrap (which is much more difficult) or downloading Bootstrap's source files locally and modifying them via use of `sass` variables see [here](https://getbootstrap.com/docs/4.0/getting-started/theming/).

## Overview of functional components

The core function of the app is `daily_menu_df()`, which queries the HUDS API and returns a `pandas` `dataframe` containing information about all menu items being served for a specified HUDS `locationId`, `date`, and `meal` (lunch/dinner). If the `doCarbonFriendly` parameter is set to `True`, then the function will return only carbon friendly menu options based on vegetarian options with at least 5 grams of protein. `daily_menu_df()` is referenced in several other functions in the app, including `grouped_menu()`, `vegetarian()`, `vegan()`, and `chicken()`.

Note that `daily_menu_df()` obtains menu items for lunch and dinner meals by parsing the `dataframe` for items whose specified `Meal_Name` contains either "lunch" or "dinner". String parsing is not the most robust solution for such a query, but this was a compromise we had to make because the naming convention for `Meal_Name` is not consistent across different HUDS locations in the API. Thus, querying specifically for "Lunch" or "Dinner" would result in unwanted omission of meal items in certain houses.

Also note that because of the way we implemented meal selection `daily_menu_df()`, Adams House dining location does not generate output for lunch. This is because there is currently no data for Adams House lunch items in the HUDS API.

The `get_locations()` function utilizes an API call to return the list of HUDS locations serving food on a given `date`. It does this by querying all meals served on a given day from the API, then isolating unique values of `Location_Name` from the `dataframe`.

Finally, the `get_date()` function returns the current date and is utilized anywhere a date input is required to dynamically update the app's information based on the current day.

### Obtaining and displaying menus in index.html

`index.html` displays the information on the HUDS Green home page and is served within the `index()` function. `index()` makes use of the `grouped_menu()` function, which first obtains a `dataframe` of meal items from `daily_menu_df()` (for a given location, time, meal, and carbon-status) and then returns a `dataframe` containing the menu items organized by their various menu categories. `pandas` allows us to do this dynamically, which is important because menu categories' names vary by location.

`index()` utilizes `grouped_menu` to obtain 4 grouped menus corresponding to lunch/dinner meals and carbon-friendly/all options, which are then passed to `index.html` to be displayed to the user.

`index.html` also receives a `locationList` variable, which contains a dynamically-updated list of currently-serving HUDS locations from the `get_locations()` function. `locationList` governs the location options displayed in the dropdown select. Obtaining the list of locations dynamically is important because operation of HUDS locations changes with the time of year/other circumstances, so only displaying currently-operational HUDS locations as options helps minimize the amount of bad/empty API calls made.

Finally, `index.html` receives a `currentLocation` variable, which contains the user-selected location (or `05` by default for Cabot/Pfoho). The location name is obtained via the `get_location_name()` function, which utilizes an API call to return the location name of a HUDS dining hall given the `locationID` (which is supplied in the HTTP POST request). `currentLocation` is displayed as the selected location.

### Generating meal recommendations in decarbonize.html and decarbonized-display.html

The Decarbonize My Meal page is displayed by `decarbonize.html` and served by `decarbonize()`. The page uses a form to collect user preferences, which are then passed to `decarbonize()` through an HTTP post request. `decarbonize()` generates 3 types of options using 3 functions: `vegetarian()`, `vegan()`, and `chicken()`, each of which utilize `daily_menu_df()` to obtain menu items and then filter those items based on their respective dietary restrictions.

`vegetarian()` filters down the dataframe to menu items that are high in protein (i.e. more than 5g/serving) and are vegetarian (`Recipe_Web_Code` contains `VGT`). Then, it sorts the dataframe in descending order. It takes the `head()` of that dataframe, where the number of rows is determined by the total protein given by 1 serving of each food. We calculate sufficient based on user input, weight and number of meals in a day, which is then matched to the Recommneded Daily Allowance of protein. In the HTML, we choose to display calorie count in addition to serving size and protein amount because we thought it was important for users to gauge what else they should be eating in addition to protein. We chose to focus on protein because protein is both the main concern for people who are considering vegetarianism and the most carbon-intensive source of food.

`vegan()` and `chicken()` function similarly, but they filter down the menu dataframe using different values (`Recipe_Web_Code` contains `VGT` for `vegan()` and all `VGT`, `chicken`, and `fish` options for `chicken()`).

Given what the user identifies as their dietary preference, we call the 3 functions accordingly. The results are then displayed back to the user in `decarbonized_display.html`, which accepts a `carbon_meal` input containing the carbon-friendly meal recommendations.
