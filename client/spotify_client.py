import base64
import os
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests

from client.spotify_auth import ClientAuth


class SpotifyAPI:
    base_url = "https://api.spotify.com/v1/"
    # client_id = None
    # client_secret = None
    # redirect_uri = None
    # auth_manager = None
    # access_token = None
    access_token_expiry = datetime.now()
    access_token_expired = True
    refresh_token = None
    refresh_token_expired = True

    def __init__(self, client_id, client_secret):
        """
        Initialises the Spotify client with the client ID and secret, using the Client Credentials flow
        """
        self.client_id = client_id
        self.client_secret = client_secret

    def __init__(self, client_id, client_secret, redirect_uri):
        """
        Initialises the Spotify client with client id, secret and redirect uri, using the Authorisation Code flow
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    @property
    def auth_manager(self):
        return self._auth_manager

    @property.setter
    def auth_manager(self, AuthManager):
        """
        Authorising client using the client credentials flow or OAuth flow depending on the presence of a redirect URI
        """
        if self.redirect_uri is None:
            self._auth_manager = ClientAuth(self.client_id, self.client_secret)
        else:
            self._auth_manager = OAuth(
                self.client_id, self.client_secret, self.redirect_uri
            )

    @property
    def access_token(self):
        self._access_token = self._auth_manager.get_access_token()

    @property
    def access_token_expiry(self):
        now = datetime.now()
        expires_in = self._auth_manager.get_token_expires_in()["expires_in"]
        self._access_token_expiry = now + timedelta(expires_in)

    # def authorise(self):
    #     self.access_token

    # def authorise(self):
    #     """
    #     Authorises the client, setting the authorisation token and returning True if successful
    #     """
    #     auth_url = self.auth_url
    #     auth_data = self.get_token_data()
    #     auth_headers = self.get_token_header()
    #     auth_response = requests.post(auth_url, data=auth_data, headers=auth_headers)
    #     if auth_response.status_code not in range(200, 299):
    #         raise Exception("Could not authenticate client")
    #         return False
    #     auth_response_data = auth_response.json()
    #     self.access_token = auth_response_data["access_token"]
    #     now = datetime.now()
    #     expires_in = auth_response_data["expires_in"]
    #     expires = now + timedelta(seconds=expires_in)
    #     self.access_token_expires = expires
    #     self.access_token_expired = expires < now
    #     return True

    # def get_access_token(self):
    #     """
    #     Returns access token if expired
    #     """
    #     token = self.access_token
    #     expiry = self.access_token_expiry
    #     now = datetime.now()
    #     if expiry < now:
    #         self.authorise()
    #         return self.access_token
    #     elif token is None:
    #         self.authorise()
    #         return self.access_token
    #     return token

    # def get_resource_header(self):
    #     """
    #     Returns headers including authorisation header derived from access token
    #     """
    #     access_token = self.get_access_token()
    #     headers = {"Authorization": f"Bearer {access_token}"}
    #     return headers

    def get_resource(self, lookup_id, resource_type="albums"):
        """
        Returns resource based on lookup ID, for resource types artists, albums, tracks etc.
        """
        base_url = self.base_url
        endpoint = f"{base_url}{resource_type}/{lookup_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def get_album(self, _id):
        """
        Returns single album resource in JSON format
        """
        return self.get_resource(_id, "albums")

    def get_artist(self, _id):
        """
        Returns single artist resource in JSON format
        """
        return self.get_resource(_id, "artists")

    def basic_search(self, query_params):
        """
        Performs basic search using query parameters
        """
        base_url = self.base_url
        endpoint = f"{base_url}search"
        headers = self.get_resource_header()
        url = f"{endpoint}?{query_params}"
        r = requests.get(url, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def search(
        self, query=None, operator=None, operator_query=None, search_type="artist"
    ):
        """
        Performs advanced search able to use dictionaries and operators as search parameters
        """
        if query == None:
            raise Exception("A search query is required")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k, v in query.items()])
        if operator != None and operator_query != None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstace(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({"q": query, "type": search_type.lower()})
        return self.basic_search(query_params)

    def get_current_user(self, resource_type="authorize"):
        endpoint = f"{self.base_url}/{resource_type}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        print(r)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()
