# Template for Flask Heroku app obtained from:
# https://stackabuse.com/deploying-a-flask-application-to-heroku/

# app.py
from flask import Flask, request, jsonify, render_template, redirect
import requests
import pandas as pd

app = Flask(__name__)

# Return dataframe containing menu items 
def daily_menu_df(date, meal, doCarbonFriendly, locationId):

    # TODO: Implement auto date query
    url = "https://go.apis.huit.harvard.edu/ats/dining/v3/recipes?date={}&locationId={}".format(date, locationId)

    payload={}
    headers = {
        'x-api-key': '8yikrfDnvJGbKKlz3pVPvAlANGPkTGza'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    dataframe = pd.DataFrame.from_dict(response.json())

    # print(response.json())

    menu_df = dataframe.loc[dataframe['Meal_Name'].str.contains(meal)]

    # Carbon friendly parsing
    if doCarbonFriendly:
        menu_df["Protein"] = menu_df["Protein"].str[:-1]

        menu_df["Protein"] = pd.to_numeric(menu_df["Protein"])

        menu_df = menu_df.loc[(menu_df['Recipe_Web_Codes'].str.contains("VGT")) & (menu_df["Protein"] >= 5)]

    return menu_df

def grouped_menu(date, meal, doCarbonFriendly, locationId):
    menu_df = daily_menu_df(date, meal, doCarbonFriendly, locationId)
    grouped = menu_df.groupby("Menu_Category_Name")
    grouped_lists = grouped["Recipe_Print_As_Name"].apply(list).reset_index()

    grouped_lists = grouped_lists.replace("eNTREES", "Entrees")
    grouped_lists = grouped_lists.replace("HALAL", "Halal")

    grouped_lists = grouped_lists.iloc[::-1]

    return grouped_lists

def vegetarian(date, meal, weight, num_meals):
    menu_df = daily_menu_df(date, meal, True, "05")
    menu_df = menu_df.loc[menu_df['Meal_Name'].str.contains(meal)]
    menu_df = menu_df.sort_values(by='Protein', ascending=False)

    protein = 0
    length = 0
    rec_protein_intake = weight * 0.36
    for index, row in menu_df.iterrows():
        while protein < rec_protein_intake / num_meals:
           protein = protein + pd.to_numeric(row['Protein'])
           length = length + 1

    vgt_df=menu_df.head(length)
    vgt_df["Calories"] = pd.to_numeric(vgt_df["Calories"])
    vgt_df['calorie total'] = vgt_df['Calories'].sum()

    return vgt_df

def vegan(date, meal, weight, num_meals):
    menu_df = daily_menu_df(date, meal, True, "05")
    menu_df = menu_df.loc[menu_df['Recipe_Web_Codes'].str.contains("VGN")]
    menu_df = menu_df.loc[menu_df['Meal_Name'].str.contains(meal)]
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

    return vgn_df

def chicken(date, meal, weight, num_meals):
    menu_df = daily_menu_df(date, meal, False, "05")
    menu_df = menu_df.loc[(menu_df['Recipe_Web_Codes'].str.contains("VGT")) | (menu_df['Recipe_Print_As_Name'].str.contains("Chicken")) | (menu_df['Recipe_Print_As_Name'].str.contains("Cod")) | (menu_df['Recipe_Print_As_Name'].str.contains("Salmon"))]
    menu_df = menu_df.loc[menu_df['Meal_Name'].str.contains(meal)]
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

    return vgn_df

def get_locations(date):
    url = "https://go.apis.huit.harvard.edu/ats/dining/v3/recipes?date={}".format(date)

    payload={}
    headers = {
        'x-api-key': '8yikrfDnvJGbKKlz3pVPvAlANGPkTGza'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    dataframe = pd.DataFrame.from_dict(response.json())


    grouped = dataframe.groupby("Location_Name")
    grouped_lists = grouped["Location_Number"].apply(list).reset_index()

    return grouped_lists

def get_location_name(locationNumber):
    url = "https://go.apis.huit.harvard.edu/ats/dining/v3/locations"

    payload={}
    headers = {
        'x-api-key': '8yikrfDnvJGbKKlz3pVPvAlANGPkTGza'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    dataframe = pd.DataFrame.from_dict(response.json())

    row_match = dataframe.loc[dataframe['location_number'] == locationNumber, "location_name"].values[0]

    return row_match

@app.route('/', methods=["GET", "POST"])
def index():

    selected_location = "05"

    if request.method == "POST":
        selected_location = request.form.get("selected_location")


    carbon_df_lunch = grouped_menu("12/13/2021", "Lunch", True, selected_location)
    carbon_df_dinner = grouped_menu("12/13/2021", "Dinner", True, selected_location)
    lunch_df = grouped_menu("12/13/2021", "Lunch", False, selected_location)
    dinner_df = grouped_menu("12/13/2021", "Dinner", False, selected_location)

    return render_template("index.html", carbon_lunch=carbon_df_lunch, carbon_dinner=carbon_df_dinner, lunch=lunch_df, dinner=dinner_df, locationList = get_locations("12/13/2021"), currentLocation=get_location_name(selected_location))

@app.route("/decarbonize", methods=["GET", "POST"])
def decarbonize():
    if request.method == "GET":
        return render_template("decarbonize.html", locationList = get_locations("12/13/2021"))
    else:
        # Get recommended protein intake
        meal = request.form.get("meal")
        weight = request.form.get("weight")
        num_meals = request.form.get("mealCount")

        if request.form.get("preferences") ==
            vegetarian("12/13/2021", meal, weight, num_meals)


        return render_template("decarbonized_display.html")

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)