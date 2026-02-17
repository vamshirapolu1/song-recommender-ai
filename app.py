from flask import Flask, render_template, request
import pandas as pd
import random
import os
import re

app = Flask(__name__)

# Load dataset
songs = pd.read_csv("songs.csv")

# Helper to get YouTube Thumbnail
def get_youtube_thumbnail(url):
    video_id = ""
    if "v=" in url:
        video_id = url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
    return f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"


# Mood detection dictionary
mood_keywords = {
    "Happy": ["happy", "joy", "fun", "smile", "celebrate",
              "cheerful", "excited", "good mood", "positive", "feel good"],

    "Sad": ["sad", "cry", "lonely", "depressed", "hurt",
            "pain", "down", "upset", "heartbroken", "low"],

    "Energetic": ["energetic", "gym", "workout", "power", "hype",
                  "adrenaline", "active", "dance hard", "pump", "intense"],

    "Chill": ["chill", "relax", "calm", "peaceful", "lofi",
              "slow", "cool vibe", "soft", "smooth", "easy"],

    "Party": ["party", "dance", "dj", "club", "celebration",
              "night", "festival vibe", "loud", "crazy", "banger"],

    "Motivational": ["motivation", "inspire", "success", "dream",
                     "goal", "hustle", "grind", "confidence", "ambition", "winner"],

    "Breakup": ["breakup", "ex", "separation", "lost love",
                "goodbye", "betrayal", "move on", "heart pain", "alone again", "relationship end"],

    "Romantic": ["love", "romantic", "crush", "couple",
                 "date", "proposal", "sweet", "valentine", "romance", "relationship"],

    "Devotional": ["god", "bhakti", "prayer", "spiritual",
                   "temple", "divine", "aarti", "mantra", "faith", "devotional"],

    "Focus": ["study", "focus", "exam", "concentrate",
              "deep work", "coding", "background music", "revision", "productivity", "work mode"],

    "Travel": ["travel", "trip", "journey", "road trip",
               "drive", "adventure", "wanderlust", "vacation", "mountain", "explore"],

    "Emotional": ["emotional", "feelings", "deep", "soul",
                  "touching", "heart", "memories", "intense", "sensitive", "inner"]
}


# Negation words
negation_words = [
    "not", "no", "never", "dont", "don't", "didn't",
    "isn't", "wasn't", "can't", "cannot", "won't"
]


# Opposite mood mapping
opposite_moods = {
    "Happy": "Sad",
    "Sad": "Happy",
    "Energetic": "Chill",
    "Chill": "Energetic",
    "Motivational": "Sad",
    "Romantic": "Breakup",
    "Breakup": "Happy",
    "Party": "Chill",
    "Focus": "Chill",
    "Travel": "Focus",
    "Emotional": "Chill",
    "Devotional": "Motivational"
}


def detect_mood(user_input):

    text = user_input.lower()

    words = re.findall(r"\w+", text)

    mood_scores = {}

    detected_negation = False

    for mood, keywords in mood_keywords.items():

        score = 0

        for keyword in keywords:

            if keyword in text:

                score += 1

                # check negation before keyword
                keyword_index = text.find(keyword)

                before_text = text[:keyword_index]

                for neg in negation_words:
                    if neg in before_text.split()[-3:]:
                        detected_negation = True
                        score -= 2   # penalize score heavily

        mood_scores[mood] = score

    best_mood = max(mood_scores, key=mood_scores.get)

    # Apply negation logic
    if detected_negation and best_mood in opposite_moods:
        return opposite_moods[best_mood]

    if mood_scores[best_mood] <= 0:
        return "Happy"

    return best_mood


@app.route("/", methods=["GET", "POST"])
def home():

    top_songs = []
    other_songs = []
    detected_mood = None
    selected_language = "All"

    if request.method == "POST":

        user_input = request.form["message"]

        selected_language = request.form.get("language", "All")

        detected_mood = detect_mood(user_input)

        filtered = songs[songs["mood"].str.lower() == detected_mood.lower()].copy()

        if selected_language != "All":
            filtered = filtered[filtered["language"].str.lower() == selected_language.lower()]

        if not filtered.empty:

            filtered['thumbnail'] = filtered['link'].apply(get_youtube_thumbnail)

            ranked = filtered[filtered["rank"] > 0].sort_values("rank")

            top_songs = ranked.head(5).to_dict(orient="records")

            others = filtered[filtered["rank"] == 0]

            if len(others) > 10:
                others = others.sample(10)

            other_songs = others.to_dict(orient="records")

    return render_template(
        "index.html",
        top_songs=top_songs,
        other_songs=other_songs,
        detected_mood=detected_mood,
        selected_language=selected_language
    )


# Render deployment block
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)