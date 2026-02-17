from flask import Flask, render_template, request
import pandas as pd
import re
import random

app = Flask(__name__)

# Load dataset
songs = pd.read_csv("songs.csv")

# ---------------- MOOD CONFIGURATION ---------------- #

mood_data = {
    "Happy": {
        "keywords": ["happy", "joy", "fun", "smile", "cheerful", "excited", "khushi", "santosham"],
        "color": "#22c55e",
        "emoji": "😊",
        "comment": "You seem happy! Let’s celebrate this mood with uplifting songs."
    },
    "Sad": {
        "keywords": ["sad", "cry", "lonely", "depressed", "bad", "udaas", "dukhi"],
        "color": "#60a5fa",
        "emoji": "😢",
        "comment": "Feeling low? These songs may help you heal or simply feel understood."
    },
    "Energetic": {
        "keywords": ["energetic", "gym", "power", "dance", "active", "josh"],
        "color": "#f97316",
        "emoji": "⚡",
        "comment": "High energy detected! Get pumped with these powerful tracks."
    },
    "Chill": {
        "keywords": ["chill", "relax", "calm", "peace", "slow", "lofi"],
        "color": "#38bdf8",
        "emoji": "😌",
        "comment": "Looks like you want to relax. Enjoy these calm and soothing songs."
    },
    "Romantic": {
        "keywords": ["love", "romantic", "crush", "relationship", "prema"],
        "color": "#ec4899",
        "emoji": "❤️",
        "comment": "Romantic mood detected! These songs match your feelings perfectly."
    }
}

# ---------------- MOOD DETECTION ---------------- #

def detect_moods(text):
    text = text.lower()
    scores = {}

    for mood, data in mood_data.items():
        score = 0
        for keyword in data["keywords"]:
            if keyword in text:
                score += 1
        scores[mood] = score

    sorted_moods = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Fallback mood
    if sorted_moods[0][1] == 0:
        return ["Happy"], 60

    primary = sorted_moods[0][0]
    moods = [primary]

    # Secondary mood (comparison)
    if len(sorted_moods) > 1 and sorted_moods[1][1] > 0:
        moods.append(sorted_moods[1][0])

    confidence = min(90, 60 + sorted_moods[0][1] * 10)

    return moods, confidence

# ---------------- ROUTE ---------------- #

@app.route("/", methods=["GET", "POST"])
def home():

    moods = []
    confidence = 0
    theme = "#020617"
    emoji = ""
    comment = ""
    recommended_songs = []

    if request.method == "POST":

        if "reset" in request.form:
            return render_template("index.html")

        user_input = request.form["message"]

        moods, confidence = detect_moods(user_input)

        primary_mood = moods[0]
        theme = mood_data[primary_mood]["color"]
        emoji = mood_data[primary_mood]["emoji"]
        comment = mood_data[primary_mood]["comment"]

        filtered = songs[songs["mood"].str.lower() == primary_mood.lower()]

        if not filtered.empty:
            recommended_songs = filtered.sample(min(5, len(filtered))).to_dict(orient="records")

    return render_template(
        "index.html",
        moods=moods,
        confidence=confidence,
        theme=theme,
        emoji=emoji,
        comment=comment,
        songs=recommended_songs
    )

if __name__ == "__main__":
    app.run(debug=True)