
# import gpt4
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

import requests
import openai as gpt4
import random as chatgpt
from pymongo import MongoClient
db_url = "mongodb+srv://bamidele:1631324de@mycluster.vffurcu.mongodb.net/?retryWrites=true&w=majority"

db_name = "prompts"

conn = MongoClient(db_url)
db = conn.get_database(db_name)
# is_subscriber, variables, owner_id
Outcomes = db.get_collection("outcomes")

ODDS_API_KEY = 'ee7e0d02a378c96a51fd63084cd240c0'
AUTO_GPT_API_KEY = 'sk-4ymsKSEYVyC41CKJqfyGT3BIbkFJMdeMP9QC3dPpwKQ2yNjB'
GPT_4_API_KEY = 'sk-4ymsKSEYVyC41CKJqfyGT3BIbkFJMdeMP9QC3dPpwKQ2yNjB'


class autogpt:
    @staticmethod
    def predict(sport, extra_parameters=None):
        try:
            gpt4.api_key = GPT_4_API_KEY

            if extra_parameters:
                response = gpt4.Completion.create(
                    model="text-davinci-003",
                    prompt=extra_parameters,
                    temperature=0.5,
                    max_tokens=50,
                    top_p=1.0,
                    frequency_penalty=0.8,
                    presence_penalty=0.0
                )
        except Exception as e:
            pass

        odds = fetch_odds_data(sport)
        prediction_in = Outcomes.find_one({"sport":sport})
        if prediction_in:
            for odd in odds:
                if odd['id'] == prediction_in['id']:
                    return prediction_in['outcome']


        if not isinstance(odds, list):
            return odds

        if len(odds) == 0:
            return "No Odds avalalaible for sport :" + sport
        data = chatgpt.choice(odds)

        bookmaker = chatgpt.choice(data['bookmakers'])
        market = chatgpt.choice(bookmaker['markets'])
        outcome = chatgpt.choice(market['outcomes'])
        # print(data['id'], outcome)
        new_prediction = {"id": data['id'], "outcome": outcome, "sport":sport}
        Outcomes.update_one(
            {"sport": sport},
            {"$set": new_prediction},
            upsert=True
        )
        return outcome


    def find_highest_odds_with_high_probability(data, min_probability=100):
        highest_odds = []
        prompts = [
            "Predict the outcome of an upcoming sporting event considering recent injuries for the athletes or teams involved.",
            "Analyze the impact of the travel schedule on the performance of athletes or teams involved in an upcoming sporting event.",
            "Evaluate the effect of crowd support on the motivation and performance of athletes or teams participating in an upcoming sporting event.",
            "Examine recent social media posts and interviews from athletes or teams involved in an upcoming sporting event to gain insights into their mental state and strategies.",
            "Predict the outcome of an upcoming sporting event by taking into account the coaching staff, recent form, home-field advantage, and other relevant factors."
        ]
        for event in data:
            for prompt in prompts:
                auto_gpt_prediction = predict_outcome_with_auto_gpt(event, prompt)
                gpt_4_prediction = predict_outcome_with_gpt_4(event, prompt)

        if auto_gpt_prediction["probability"] >= min_probability and gpt_4_prediction["probability"] >= min_probability:
            highest_odds.append({
                "event": event,
                "auto_gpt_prediction": auto_gpt_prediction,
                "gpt_4_prediction": gpt_4_prediction
            })
            return highest_odds




def fetch_odds_data(sport):
    url = f'https://api.the-odds-api.com/v4/sports/{sport}/odds'
    params = {
    'apiKey': "ee7e0d02a378c96a51fd63084cd240c0",
    'regions': 'us,uk,eu,au',
    'oddsFormat': 'decimal'
    }
    response = requests.get(url, params=params)
    return response.json()


def collect_data():
    sports = [
    'soccer_epl',
    'basketball_nba',
    'americanfootball_nfl',
    'baseball_mlb',
    'icehockey_nhl',
    'tennis_atp',
    'golf_pga',
    'boxing',
    'mma'
    ]

    data = []
    for sport in sports:
        odds_data = fetch_odds_data(sport)
        data.extend(odds_data)
        return data


def predict_outcome_with_auto_gpt(event, prompt):
    # Replace this with your actual implementation to predict outcomes using AutoGPT
    # Use the provided prompt for prediction
    prediction = autogpt.predict(prompt)
    return {"winner": prediction[0], "probability": prediction[1]}


def predict_outcome_with_gpt_4(event, prompt):
    # Replace this with your actual implementation to predict outcomes using GPT-4
    # Use the provided prompt for prediction
    prediction = autogpt(prompt)
    return {"winner": prediction[0], "probability": prediction[1]}



def predict_match():
    sports = [
    'soccer_epl',
    'basketball_nba',
    'americanfootball_nfl',
    'baseball_mlb',
    'icehockey_nhl',
    'tennis_atp',
    'golf_pga',
    'boxing',
    'mma'
    ]
    print("prediction started ...................")

    for sport in sports:
        prediction = autogpt.predict(sport)
        print(prediction)

    print("prediction Ended .................")

@app.route('/', methods=['GET'])
def predict_view():
    sports = [
    'soccer_epl',
    'basketball_nba',
    'americanfootball_nfl',
    'baseball_mlb',
    'icehockey_nhl',
    'tennis_atp',
    'golf_pga',
    'boxing',
    'mma'
    ]
    print("prediction started ...................")
    response = "Prediction Result ======================= <br/> <br/>"
    for sport in sports:
        prediction = autogpt.predict(sport)
        response += f"sport => {sport}, prediction result ==> {prediction} <br/>"

    return response



if __name__ == '__main__':
    app.run(port=5000, debug=True)