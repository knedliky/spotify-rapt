import os
from pathlib import Path

import pandas as pd
import streamlit as st

from client.spotify_client import *

current_dir = Path.cwd()
home_dir = Path.home()


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css(current_dir / "style" / "style.css")

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
s = SpotifyAPI(client_id, client_secret)

features = (
    "acousticness",
    "danceability",
    "energy",
    "instrumentalness",
    "liveness",
    "loudness",
    "speechiness",
    "tempo",
    "valence",
)

st.title("Spotify Features App")
st.header(s.get_current_user())
artist_name = st.text_input("Artist Name")
featuring = st.selectbox("Feature", features)
button_clicked = st.button("OK")

data = s.search({"artist": f"{artist_name}"}, search_type="track")

need = []
for i, item in enumerate(data["tracks"]["items"]):
    track = item["album"]
    track_id = item["id"]
    song_name = item["name"]
    popularity = item["popularity"]
    need.append(
        (
            i,
            track["artists"][0]["name"],
            track,
            track_id,
            song_name,
            track["release_date"],
            popularity,
        )
    )

track_df = pd.DataFrame(
    need,
    index=None,
    columns=(
        "item",
        "artist",
        "album_name",
        "id",
        "song_name",
        "release_date",
        "popularity",
    ),
)
