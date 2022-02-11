import base64
import os
import webbrowser
from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlencode, urlparse

import requests


class SpotifyClient:
    BASE_URL = "https://api.spotify.com/v1"

    def __init__(
        self, client_id, client_secret, redirect_uri=None, scope=None, state=None
    ):
        self._auth_manager = AuthManager(client_id, client_secret, redirect_uri, scope)

    @property
    def client_credentials(self):
        client_credentials = f"{self._client_id}:{self._client_secret}"
        self._client_credentials = base64.b64encode(client_credentials.encode())
        return self._client_credentials.decode()

    @property
    def token_info(self):
        return self._token_info

    @token_info.setter
    def token_info(self, val):
        # Assert if this is a valid token?
        self._token_info = val

    @property
    def auth_manager(self):
        return self._auth_manager

    @auth_manager.setter
    def auth_manager(self, val):
        if isinstance(val, AuthManager):
            self._auth_manager = val

    def authorise(self):
        self.token_info = self.auth_manager.request_token()

    @property
    def resource_headers(self):
        access_token = self.token_info.get("access_token")
        return {"Authorization": f"Bearer {access_token}"}

    def get_resource(self, lookup_id, resource_type="albums"):
        """
        Returns resource based on lookup ID, for artists, albums and tracks (so far)
        """
        endpoint = f"{self.BASE_URL}/{resource_type}/{lookup_id}"
        headers = self.resource_headers
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def get_album(self, _id):
        """
        Returns a single album resource
        """
        return self.get_resource(_id, "albums")

    def get_artist(self, _id):
        """
        Returns a single artist resource
        """
        return self.get_resource(_id, "artists")

    def basic_search(self, query_params):
        """
        Performs basic search using query parameters
        """
        endpoint = f"{self.BASE_URL}/search"
        headers = self.resource_headers
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


class AuthManager:
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    AUTH_URL = "https://accounts.spotify.com/authorize"

    def __init__(
        self, client_id, client_secret, redirect_uri=None, scope=None, state=None
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._scope = scope
        self._state = state

    @property
    def client_id(self):
        return self._client_id

    @property
    def client_secret(self):
        return self._client_secret

    @property
    def redirect_uri(self):
        return self._redirect_uri

    @property
    def scope(self):
        return self._scope

    @property
    def state(self):
        return self._state

    @property
    def client_credentials(self):
        client_credentials = f"{self._client_id}:{self._client_secret}"
        self._client_credentials = base64.b64encode(client_credentials.encode())
        return self._client_credentials.decode()

    @property
    def redirect_uri(self):
        return self._redirect_uri

    # Add setter for scope and validate
    @property
    def scope(self):
        return self._scope

    @property
    def grant_type(self):
        if not self._redirect_uri:
            return {"grant_type": "client_credentials"}
        return {"grant_type": "authorization_code"}

    @property
    def basic_auth(self):
        return {"Authorization": f"Basic {self.client_credentials}"}

    @property
    def content_type(self):
        return {"content_type": "application/x-www-form-urlencoded"}

    @property
    def token_data(self):
        return {
            "code": self.code,
            "state": self.state,
            "redirect_uri": self.redirect_uri,
        } | self.grant_type

    # Change this to just be auth when merging the basic and bearer auth tokens
    @property
    def token_headers(self):
        return self.basic_auth | self.content_type

    @property
    def auth_url(self):
        query = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
        }
        if self.scope:
            query["scope"] = self.scope
        if self.state is None:
            query["state"] = self.state
        # if self.show_dialog:
        #     payload["show_dialog"] = True
        urlparams = urlencode(query)
        return f"{self.AUTH_URL}?{urlparams}"

    def authorise(self):
        url = webbrowser.open(self.auth_url)
        print(url)
        # _, code = AuthManager.parse_auth_url(url)

    def request_token(self, code=None):
        url = self.TOKEN_URL
        data = self.token_data
        # if code is not None:
        #     data = data | {"code":code, "redirect_uri":self.redirect_uri}
        headers = self.token_headers
        print(url, data, headers)
        r = requests.post(url, data=data, headers=headers)
        if r.status_code not in range(200, 299):
            raise Exception(
                f"Could not authenticate user, please try again. Error code: {r.status_code}"
            )
        return r.json()

    @staticmethod
    def parse_auth_url(url):
        query = urlparse(url).query
        form = parse_qs(query)
        if "error" in form:
            raise Exception("Error authorising user")
        return tuple(form.get(param) for param in ["state", "code"])

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, val):
        self._code = val

    @property
    def state(self):
        return self._state
