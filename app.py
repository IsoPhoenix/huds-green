# Template for Flask Heroku app obtained from:
# https://stackabuse.com/deploying-a-flask-application-to-heroku/

# app.py
from flask import Flask, request, jsonify, render_template, redirect
import requests
import pandas as pd

app = Flask(__name__)

def daily_menu_df(date):
    url = "https://go.apis.huit.harvard.edu/ats/dining/v3/recipes?locationId=05&date={}".format(date)

    payload={}
    headers = {
        'x-api-key': '8yikrfDnvJGbKKlz3pVPvAlANGPkTGza'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    dataframe = pd.DataFrame.from_dict(response.json())

    # print(response.json())

    output = dataframe.loc[dataframe['Meal_Name'].str.contains("Lunch Entrees")]

    return output

@app.route('/getmsg/', methods=['GET'])
def respond():
    # Retrieve the name from url parameter
    name = request.args.get("name", None)

    # For debugging
    print(f"got name {name}")

    response = {}

    # Check if user sent a name at all
    if not name:
        response["ERROR"] = "no name found, please send a name."
    # Check if the user entered a number not a name
    elif str(name).isdigit():
        response["ERROR"] = "name can't be numeric."
    # Now the user entered a valid name
    else:
        response["MESSAGE"] = f"Welcome {name} to our awesome platform!!"

    # Return the response in json format
    return jsonify(response)

@app.route('/post/', methods=['POST'])
def post_something():
    param = request.form.get('name')
    print(param)
    # You can add the test cases you made in the previous function, but in our case here you are just testing the POST functionality
    if param:
        return jsonify({
            "Message": f"Welcome {name} to our awesome platform!!",
            # Add this option to distinct the POST request
            "METHOD" : "POST"
        })
    else:
        return jsonify({
            "ERROR": "no name found, please send a name."
        })

# A welcome message to test our server
@app.route('/')
def index():

    menu_df = daily_menu_df("12/13/2021")
    grouped = menu_df.groupby("Menu_Category_Name")
    grouped_lists = grouped["Recipe_Print_As_Name"].apply(list).reset_index()

    grouped_lists = grouped_lists.replace("eNTREES", "Entrees")
    grouped_lists = grouped_lists.replace("HALAL", "Halal")

    grouped_lists = grouped_lists.iloc[::-1]

    return render_template("index.html", menu=grouped_lists)

@app.route("/decarbonize", methods=["GET", "POST"])
def decarbonize():
    if request.method == "GET":
        return render_template("decarbonize.html")
    else:
        # Do stuff
        return redirect("/")

# @app.route("/test", methods=["GET"])
# def test():
#     url = "https://go.apis.huit.harvard.edu/ats/dining/v3/events?locationId=05&date=12/13/2021"

#     payload={}
#     headers = {
#         'x-api-key': '8yikrfDnvJGbKKlz3pVPvAlANGPkTGza'
#     }

#     response = requests.request("GET", url, headers=headers, data=payload)

#     print(response.json())
#     return redirect("/")


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)