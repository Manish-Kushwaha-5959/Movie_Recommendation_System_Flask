from flask import Flask, render_template, request, jsonify
import pandas as pd
import requests
import pickle

app = Flask(__name__)

# Load movie data and similarity model
movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
model_dict = pickle.load(open('model_dict.pkl', 'rb'))

movie_data = pd.DataFrame(movie_dict)
movie_model = pd.DataFrame(model_dict)

# Function to fetch movie poster
def fetch_poster(movie_id):
    api_key = "d503008795377effc30c0fe86fda10c4"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        file = response.json()
        return f"https://image.tmdb.org/t/p/w500{file.get('poster_path', '')}"
    return ""

# Recommendation function
def recommend(movie):
    try:
        idx = movie_data[movie_data["title"] == movie].index[0]
        distance = movie_model.loc[idx]
        movie_list = sorted(enumerate(distance), reverse=True, key=lambda x: x[1])[1:7]

        recommendations = []
        for j in movie_list:
            movie_id = movie_data.movie_id[j[0]]
            recommendations.append({
                "title": movie_data.title[j[0]],
                "poster": fetch_poster(movie_id)
            })
        return recommendations
    except IndexError:
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        movie_name = request.form["movie_name"]
        recommendations = recommend(movie_name)
        return render_template("index.html", movie_name=movie_name, recommendations=recommendations, movies=movie_data["title"].tolist())
    
    return render_template("index.html", movie_name=None, recommendations=None, movies=movie_data["title"].tolist())

if __name__ == "__main__":
    app.run(debug=True)
