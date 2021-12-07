# Template for Flask Heroku app obtained from:
# https://stackabuse.com/deploying-a-flask-application-to-heroku/

# app.py
from flask import Flask, request, jsonify, render_template, redirect
import requests
import pandas as pd

app = Flask(__name__)

# Return dataframe containing menu items 
def daily_menu_df(date, meal, doCarbonFriendly):

    # TODO: Implement auto date query
    url = "https://go.apis.huit.harvard.edu/ats/dining/v3/recipes?locationId=05&date={}".format(date)

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

def vegetarian():
    menu_df = carbon_friendly_menu("12/13/2021")
    menu_df = menu_df.loc[menu_df['Meal_Name'].str.contains("Lunch Entrees")]
    menu_df = menu_df.sort_values(by='Protein', ascending=False)

    protein = 0
    length = 0
    for index, row in menu_df.iterrows():
        while protein < 50 / 2:
           protein = protein + pd.to_numeric(row['Protein'])
           length = length + 1

    vgt_df=menu_df.head(length)
    vgt_df["Calories"] = pd.to_numeric(vgt_df["Calories"])
    vgt_df['calorie total'] = vgt_df['Calories'].sum()

    return vgt_df

def vegan():
    menu_df = carbon_friendly_menu("12/13/2021")
    menu_df = menu_df.loc[menu_df['Recipe_Web_Codes'].str.contains("VGN")]
    menu_df = menu_df.loc[menu_df['Meal_Name'].str.contains("Lunch Entrees")]
    menu_df = menu_df.sort_values(by='Protein', ascending=False)

    protein = 0
    length = 0
    for index, row in menu_df.iterrows():
        while protein < 50 / 2:
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

    carbon_df_lunch = daily_menu_df("12/13/2021", "Lunch", True)
    carbon_df_dinner = daily_menu_df("12/13/2021", "Dinner", True)
    lunch_df = daily_menu_df("12/13/2021", "Lunch", False)
    dinner_df = daily_menu_df("12/13/2021", "Dinner", False)

    selected_location = "05"

    if request.method == "POST":
        selected_location = request.form.get("selected_location")

    return render_template("index.html", carbon_lunch=carbon_df_lunch, carbon_dinner=carbon_df_dinner, lunch=lunch_df, dinner=dinner_df, locationList = get_locations("12/13/2021"), currentLocation=get_location_name(selected_location))
@app.route("/decarbonize", methods=["GET", "POST"])
def decarbonize():
    if request.method == "GET":
        return render_template("decarbonize.html")
    else:
        # Get recommended protein intake
        weight = request.form.get("weight")
        rec_protein_intake = 0.36 * weight

        return redirect("/")

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)