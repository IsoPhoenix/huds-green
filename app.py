# Template for Flask Heroku app obtained from:
# https://stackabuse.com/deploying-a-flask-application-to-heroku/

# app.py
from flask import Flask, request, jsonify, render_template, redirect
import requests
import pandas as pd
from datetime import date

app = Flask(__name__)

# Global creation of current date
def get_date():
    current_date = date.today()
    return current_date.strftime("%m/%d/%Y")

# Return dataframe containing today's menu items 
def daily_menu_df(date, meal, doCarbonFriendly, locationId):

    # Call HUDS menu using HUIT Dining API
    url = "https://go.apis.huit.harvard.edu/ats/dining/v3/recipes?date={}&locationId={}".format(date, locationId)

    payload={}
    headers = {
        'x-api-key': '8yikrfDnvJGbKKlz3pVPvAlANGPkTGza'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    dataframe = pd.DataFrame.from_dict(response.json())

    # Create dataframe of daily meals
    menu_df = dataframe.loc[dataframe['Meal_Name'].str.contains(meal, case=False)]

    # Carbon friendly parsing
    if doCarbonFriendly:
    
        # Convert column protein to a float for comparison
        menu_df["Protein"] = menu_df["Protein"].str[:-1]

        menu_df["Protein"] = pd.to_numeric(menu_df["Protein"])

        # Filter dataframe for only vegetarian options with at least 5 grams of protein
        menu_df = menu_df.loc[(menu_df['Recipe_Web_Codes'].str.contains("VGT")) & (menu_df["Protein"] >= 5)]

    return menu_df

# Return dataframe of today's menu, grouped by menu category and cleaned for HTML display
def grouped_menu(date, meal, doCarbonFriendly, locationId):
    menu_df = daily_menu_df(date, meal, doCarbonFriendly, locationId)
    grouped = menu_df.groupby("Menu_Category_Name")
    grouped_lists = grouped["Recipe_Print_As_Name"].apply(list).reset_index()

    grouped_lists = grouped_lists.replace("eNTREES", "Entrees")
    grouped_lists = grouped_lists.replace("HALAL", "Halal")

    grouped_lists = grouped_lists.iloc[::-1]

    return grouped_lists

# Return dataframe of options for vegetarians or people willing to eat vegetarian with sufficient protein
def vegetarian(date, meal, weight, num_meals, locationId):
    menu_df = daily_menu_df(date, meal, True, locationId)
    menu_df = menu_df.loc[menu_df['Meal_Name'].str.contains(meal, case=False)]
    menu_df = menu_df.sort_values(by='Protein', ascending=False)

    protein = 0
    length = 0
    # RDA recommends 0.36g of protein per lb of body weight
    rec_protein_intake = weight * 0.36

    # Select most protein-intensive options until rec protein intake is met 
    for index, row in menu_df.iterrows():
        # Divide daily protein intake by number of substantial meals for meal protein intake
        while protein < rec_protein_intake / num_meals:
           protein = protein + pd.to_numeric(row['Protein'])
           length = length + 1

    # Create a dataframe of recommended protein options
    vgt_df=menu_df.head(length)

    # Add a column for total calories from eating 1 serving of each option in df
    vgt_df["Calories"] = pd.to_numeric(vgt_df["Calories"])
    vgt_df['calorie total'] = vgt_df['Calories'].sum()

    # Further clean df for HTML display
    vgt_df = vgt_df.replace("eNTREES", "Entrees")
    vgt_df = vgt_df.replace("HALAL", "Halal")

    return vgt_df

# Return dataframe of options for vegans with sufficient protein
def vegan(date, meal, weight, num_meals, locationId):
    menu_df = daily_menu_df(date, meal, True, locationId)

    # Function is similar to VGT fcn, but parses for only vegan options
    menu_df = menu_df.loc[menu_df['Recipe_Web_Codes'].str.contains("VGN")]
    menu_df = menu_df.loc[menu_df['Meal_Name'].str.contains(meal, case=False)]
    menu_df = menu_df.sort_values(by='Protein', ascending=False)

    protein = 0
    length = 0
    rec_protein_intake = weight * 0.36
    for index, row in menu_df.iterrows():
        while protein < rec_protein_intake / num_meals:
           protein = protein + pd.to_numeric(row['Protein'])
           length = length + 1

    vgn_df=menu_df.head(length)
    vgn_df["Calories"] = pd.to_numeric(vgn_df["Calories"])
    vgn_df['calorie total'] = vgn_df['Calories'].sum()

    vgn_df = vgn_df.replace("eNTREES", "Entrees")
    vgn_df = vgn_df.replace("HALAL", "Halal")

    return vgn_df

# Return dataframe of options for people who want to eat meat, but are willing to give up red meat
def chicken(date, meal, weight, num_meals, locationId):
    menu_df = daily_menu_df(date, meal, False, locationId)

    # Since doCarbonFriendly is false, convert Protein column to float for comparison
    menu_df["Protein"] = menu_df["Protein"].str[:-1]
    menu_df["Protein"] = pd.to_numeric(menu_df["Protein"])

    # Parse for options that are VGT or contain chicken or fish
    menu_df = menu_df.loc[(menu_df['Recipe_Web_Codes'].str.contains("VGT")) | (menu_df['Recipe_Print_As_Name'].str.contains("Chicken", case=False)) | (menu_df['Recipe_Print_As_Name'].str.contains("Cod", case=False)) | (menu_df['Recipe_Print_As_Name'].str.contains("Salmon", case=False))]
    menu_df = menu_df.loc[menu_df['Meal_Name'].str.contains(meal, case=False)]

    # Order by most protein-intensive option
    menu_df = menu_df.sort_values(by='Protein', ascending=False)

    # The rest of chicken() is the same as the VGN and VGT fcns
    protein = 0
    length = 0
    rec_protein_intake = weight * 0.36
    for index, row in menu_df.iterrows():
        while protein < rec_protein_intake / num_meals:
           protein = protein + pd.to_numeric(row['Protein'])
           length = length + 1

    # Create a dataframe of recommended protein options, including nonred meats
    chicken_df=menu_df.head(length)
    chicken_df["Calories"] = pd.to_numeric(chicken_df["Calories"])
    chicken_df['calorie total'] = chicken_df['Calories'].sum()

    chicken_df = chicken_df.replace("eNTREES", "Entrees")
    chicken_df = chicken_df.replace("HALAL", "Halal")

    return chicken_df

# Get menus for each HUDS dining hall based on DATE
def get_locations(date):

    # Call HUIT Dining API
    url = "https://go.apis.huit.harvard.edu/ats/dining/v3/recipes?date={}".format(date)

    payload={}
    headers = {
        'x-api-key': '8yikrfDnvJGbKKlz3pVPvAlANGPkTGza'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    dataframe = pd.DataFrame.from_dict(response.json())

    # Create dataframe grouped by dining location
    grouped = dataframe.groupby("Location_Name")
    grouped_lists = grouped["Location_Number"].apply(list).reset_index()

    return grouped_lists

# Get menus for each HUDS dining hall based on LOCATION
def get_location_name(locationNumber):

    # Call HUIT Dining API
    url = "https://go.apis.huit.harvard.edu/ats/dining/v3/locations"

    payload={}
    headers = {
        'x-api-key': '8yikrfDnvJGbKKlz3pVPvAlANGPkTGza'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    dataframe = pd.DataFrame.from_dict(response.json())

    # Return only the menu for a given dining location
    row_match = dataframe.loc[dataframe['location_number'] == locationNumber, "location_name"].values[0]

    return row_match

# Home page
@app.route('/', methods=["GET", "POST"])
def index():

    # Default to today's menu at Cabot and Pfoho
    selected_location = "05"

    # If user changes dining locatioon
    if request.method == "POST":
        selected_location = request.form.get("selected_location")

    # Create 4 dfs: carbon-friendly lunch and dinner options, and all lunch and dinner options
    carbon_df_lunch = grouped_menu(get_date(), "Lunch", True, selected_location)
    carbon_df_dinner = grouped_menu(get_date(), "Dinner", True, selected_location)
    lunch_df = grouped_menu(get_date(), "Lunch", False, selected_location)
    dinner_df = grouped_menu(get_date(), "Dinner", False, selected_location)

    # Pull dfs into HTML for homepage
    return render_template("index.html", carbon_lunch=carbon_df_lunch, carbon_dinner=carbon_df_dinner, lunch=lunch_df, dinner=dinner_df, locationList = get_locations(get_date()), currentLocation=get_location_name(selected_location))

# Decarbonize My Meal page
@app.route("/decarbonize", methods=["GET", "POST"])
def decarbonize():

    # Display form for user dietary preferences
    if request.method == "GET":
        return render_template("decarbonize.html", locationList = get_locations(get_date()))

    # When user submits form   
    else:
        # Get what meal they would like to see options for
        meal = request.form.get("meal")

        # Get recommended protein intake
        weight = int(request.form.get("weight"))

        # Get number of substantial meals in a day
        num_meals = int(request.form.get("mealCount"))

        # Get whether they will be eating VGT, VGN, or nonredmeats
        prefs = request.form.get("preferences")

        # Get preferred dining location
        location = request.form.get("selected_location")

        # If user declares vegetarian or willing to be vegetarian today
        if prefs == "1" or prefs == "2":
            # Call vegetarian function
            carbon_df = vegetarian(get_date(), meal, weight, num_meals, location)

        # If user declares vegan
        elif prefs == "0":
            # Call vegan function
            carbon_df = vegan(get_date(), meal, weight, num_meals, location)

        # If user declares they are willing to avoid red meats
        elif prefs == "3":
            # Call chicken function
            carbon_df = chicken(get_date(), meal, weight, num_meals, location)

        # Return df as recommended meal displayed in HTML
        return render_template("decarbonized_display.html", carbon_meal = carbon_df)

# About page
@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)