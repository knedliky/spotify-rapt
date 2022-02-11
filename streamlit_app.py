import os

import streamlit as st

from client.spotify_client import *

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
scopes = ["user-read-top"]
spotify = SpotifyClient(client_id, client_secret, redirect_uri)

urlparams = st.experimental_get_query_params()

if "code" in urlparams:
    spotify.auth_manager.code = urlparams["code"]
    st.write(spotify.auth_manager.code)
    st.write(st.session_state["access_token"])
    spotify.access_token = spotify.auth_manager.request_token()
    st.session_state["access_token"] = spotify.access_token
    # session_state['signed_in'] = True

if "access_token" not in st.session_state:
    st.write(
        "No tokens found for this session. Please log in by clicking the link below."
    )
    link_html = ' <a target="_self" href="{url}" >{msg}</a> '.format(
        url=spotify.auth_manager.auth_url, msg="Click me to authenticate!"
    )
    st.markdown(link_html, unsafe_allow_html=True)

st.write(st.session_state)
# st.write(spotify.get_current_user())
