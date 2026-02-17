from flask import Flask, render_template, request
import pandas as pd
import random
import os
import re

app = Flask(__name__)

songs = pd.read_csv("songs.csv").fillna("")


def get_youtube_thumbnail(url):
    video_id = ""
    if "v=" in url:
        video_id = url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
    return f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"

mood_keywords = {
    "Happy": ["happy","joy","fun","smile","celebrate"],
    "Sad": ["sad","cry","lonely","depressed","hurt"],
    "Energetic": ["energetic","gym","workout","power"],
    "Chill": ["chill","relax","calm","peaceful"],
    "Romantic": ["love","romantic","crush"],
    "Focus": ["study","focus","exam"],
}

negation_words = ["not","no","never","dont","don't"]

opposite_moods = {
    "Happy":"Sad",
    "Sad":"Happy",
    "Energetic":"Chill",
    "Chill":"Energetic"
}

def detect_mood(user_input):

    text = user_input.lower()
    words = re.findall(r"\w+", text)

    for i, word in enumerate(words):
        if word in negation_words:
            for j in range(i+1,min(i+4,len(words))):
                next_word = words[j]
                for mood, keywords in mood_keywords.items():
                    if next_word in keywords:
                        return opposite_moods.get(mood,"Sad"),75

    mood_scores = {}

    for mood, keywords in mood_keywords.items():
        score=0
        for keyword in keywords:
            if keyword in text:
                score+=1
        mood_scores[mood]=score

    best_mood=max(mood_scores,key=mood_scores.get)
    confidence=min(95,50+(mood_scores[best_mood]*15))

    if mood_scores[best_mood]==0:
        return "Happy",50

    return best_mood,confidence


@app.route("/", methods=["GET","POST"])
def home():

    top_songs=[]
    other_songs=[]
    detected_mood=None
    confidence=None
    selected_language="All"
    mode="video"

    if request.method=="POST":

        user_input=request.form["message"]
        selected_language=request.form.get("language","All")

        detected_mood,confidence=detect_mood(user_input)

        filtered=songs[songs["mood"].str.lower()==detected_mood.lower()].copy()

        if selected_language!="All":
            filtered=filtered[filtered["language"].str.lower()==selected_language.lower()]

        if not filtered.empty:

            filtered['thumbnail']=filtered['link'].apply(get_youtube_thumbnail)

            ranked=filtered[filtered["rank"]>0].sort_values("rank")
            top_songs=ranked.head(5).to_dict(orient="records")

            others=filtered[filtered["rank"]==0]

            if len(others)>10:
                others=others.sample(10)

            other_songs=others.to_dict(orient="records")

        return render_template(
    "index.html",
    top_songs=top_songs,
    other_songs=other_songs,
    detected_mood=detected_mood,
    confidence=confidence,
    selected_language=selected_language,
)


if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)