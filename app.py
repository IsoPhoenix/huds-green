# Template for Flask Heroku app obtained from:
# https://stackabuse.com/deploying-a-flask-application-to-heroku/

# app.py
from flask import Flask, request, jsonify, render_template, redirect
import requests
import pandas as pd

app = Flask(__name__)

# Return dataframe containing menu items 
def daily_menu_df(date, meal):

    # TODO: Implement auto date query
    url = "https://go.apis.huit.harvard.edu/ats/dining/v3/recipes?locationId=05&date={}".format(date)

    payload={}
    headers = {
        'x-api-key': '8yikrfDnvJGbKKlz3pVPvAlANGPkTGza'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    dataframe = pd.DataFrame.from_dict(response.json())

    # print(response.json())

    output = dataframe.loc[dataframe['Meal_Name'].str.contains(meal)]

    return output

def menu_grouped(date, meal):
    menu_df = daily_menu_df(date, meal)
    grouped = menu_df.groupby("Menu_Category_Name")
    grouped_lists = grouped["Recipe_Print_As_Name"].apply(list).reset_index()

    grouped_lists = grouped_lists.replace("eNTREES", "Entrees")
    grouped_lists = grouped_lists.replace("HALAL", "Halal")

    grouped_lists = grouped_lists.iloc[::-1]

    return grouped_lists

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

@app.route('/')
def index():

    # Format menu DF into grouped list by dish category
    lunch_df = menu_grouped("12/13/2021", "Lunch")
    dinner_df = menu_grouped("12/13/2021", "Dinner")

    return render_template("index.html", lunch=lunch_df, dinner=dinner_df, locationList = get_locations("12/13/2021"))

@app.route("/decarbonize", methods=["GET", "POST"])
def decarbonize():
    if request.method == "GET":
        return render_template("decarbonize.html")
    else:
        # Do stuff
        return redirect("/")

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)