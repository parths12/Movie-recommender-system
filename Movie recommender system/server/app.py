import pickle

import streamlit as st


# ... (previous code)
import streamlit as st
import requests
import pickle
import streamlit as st
import requests
import pandas as pd
import time

# Function to fetch movie poster with error handling and retry logic
def fetch_poster(movie_id):
    MAX_RETRIES = 3
    retries = 0
    while retries < MAX_RETRIES:
        try:
            url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(
                movie_id)
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path is not None:
                return "https://image.tmdb.org/t/p/w500/" + poster_path
            else:
                return None
        except requests.RequestException as e:
            retries += 1
            st.warning(f"Failed to fetch poster (Attempt {retries}/{MAX_RETRIES}). Error: {e}")
            if retries < MAX_RETRIES:
                st.warning("Retrying...")
                time.sleep(2)  # Wait for a few seconds before retrying
            else:
                st.error("Max retries exceeded. Unable to fetch poster.")
                return None

# Function to recommend movies
def recommend(movie, movies, similarity):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]]['movie_id']
        poster = fetch_poster(movie_id)

        if poster is not None:
            recommended_movie_posters.append(poster)
            recommended_movie_names.append(movies.iloc[i[0]]['title'])

    return recommended_movie_names, recommended_movie_posters

# Streamlit App
st.header('Movie Recommender System')

movies_data = pickle.load(open('movie_list.pkl', 'rb'))
similarity_data = pickle.load(open('cosine_similarity.pkl', 'rb'))

movie_list = movies_data['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list,
    key="movie_selector"
)

if st.button('Show Recommendation', key="recommendation_button"):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies_data, similarity_data)
    col1, col2, col3, col4, col5 = st.columns(5)
    for col, name, poster in zip([col1, col2, col3, col4, col5], recommended_movie_names, recommended_movie_posters):
        col.text(name)
        col.image(poster)
