from flask import Flask, render_template, request
import pandas as pd
import random
import re

app = Flask(__name__)

songs = pd.read_csv("songs.csv")

# ---------------- MOOD DATA ---------------- #

mood_data = {
    "Happy": {
        "emoji": "😊",
        "color": "#22c55e",
        "comment": "You seem happy! Enjoy these feel-good songs 🎶",
        "keywords": ["happy", "joy", "excited", "fun", "cheerful", " ఆనందం", "ఖుషి", "खुश"]
    },
    "Sad": {
        "emoji": "😢",
        "color": "#60a5fa",
        "comment": "Feeling sad? These songs will understand you 💙",
        "keywords": ["sad", "cry", "down", "lonely", "bad", "దుఃఖం", "బాధ", "उदास"]
    },
    "Energetic": {
        "emoji": "⚡",
        "color": "#facc15",
        "comment": "High energy mode ON! 🔥",
        "keywords": ["gym", "workout", "power", "energetic", "dance", "ఉత్సాహం", "जोश"]
    },
    "Chill": {
        "emoji": "😌",
        "color": "#a855f7",
        "comment": "Relax and breathe. Chill vibes only 🌙",
        "keywords": ["relax", "calm", "peace", "chill", "slow", "ప్రశాంతం", "शांत"]
    }
}

# ---------------- MOOD DETECTION ---------------- #

def detect_moods(text):
    text = text.lower()
    scores = {}

    for mood, data in mood_data.items():
        score = sum(1 for k in data["keywords"] if k in text)
        if score > 0:
            scores[mood] = score

    sorted_moods = sorted(scores, key=scores.get, reverse=True)

    if not sorted_moods:
        return ["Happy"], 40

    confidence = min(90, scores[sorted_moods[0]] * 30)
    return sorted_moods[:2], confidence


# ---------------- ROUTE ---------------- #

@app.route("/", methods=["GET", "POST"])
def home():
    detected_moods = []
    confidence = 0
    theme = "#020617"
    emoji = ""
    comment = ""
    top_songs = []
    other_songs = []
    selected_language = "All"

    if request.method == "POST":
        text = request.form.get("message", "")
        selected_language = request.form.get("language", "All")

        detected_moods, confidence = detect_moods(text)
        main_mood = detected_moods[0]

        mood_info = mood_data[main_mood]
        theme = mood_info["color"]
        emoji = mood_info["emoji"]
        comment = mood_info["comment"]

        filtered = songs[songs["mood"] == main_mood]

        if selected_language != "All":
            filtered = filtered[filtered["language"] == selected_language]

        filtered = filtered.sample(frac=1)

        top_songs = filtered.head(5).to_dict(orient="records")
        other_songs = filtered.iloc[5:10].to_dict(orient="records")

    return render_template(
        "index.html",
        moods=detected_moods,
        confidence=confidence,
        theme=theme,
        emoji=emoji,
        comment=comment,
        top_songs=top_songs,
        other_songs=other_songs,
        selected_language=selected_language
    )


if __name__ == "__main__":
    app.run(debug=True)