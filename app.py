from flask import Flask, render_template, request
import pandas as pd
import pickle
import requests

app = Flask(__name__)

# Load only movie_dict at startup (small in size)
movie_dict = pickle.load(open("movie_dict.pkl", "rb"))
movie_data = pd.DataFrame(movie_dict)

def load_model():
    """Loads the similarity model only when needed to save memory"""
    return pickle.load(open("model_dict.pkl", "rb"))

def fetch_poster(movie_id):
    """Fetch movie poster from TMDB API"""
    api_key = "d503008795377effc30c0fe86fda10c4"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        file = response.json()
        return "https://image.tmdb.org/t/p/w500" + file.get("poster_path", "")
    return ""

def recommend(movie):
    """Recommend 5 similar movies"""
    try:
        idx = movie_data[movie_data.title == movie].index[0]

        # Load model only when needed
        movie_model = pd.DataFrame(load_model())

        # Get similarity scores
        distances = movie_model.loc[idx]
        movie_list = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)[1:6]

        recommended_movies = []
        posters = []

        for i in movie_list:
            movie_id = movie_data.movie_id[i[0]]
            recommended_movies.append(movie_data.title[i[0]])
            posters.append(fetch_poster(movie_id))

        return recommended_movies, posters

    except IndexError:
        return [], []  # If movie is not found, return empty list

@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = []
    posters = []
    
    if request.method == "POST":
        movie_name = request.form.get("movie")
        recommendations, posters = recommend(movie_name)
    
    return render_template("index.html", movies=movie_data["title"].tolist(), recommendations=recommendations, posters=posters)

if __name__ == "__main__":
    app.run(debug=True)
