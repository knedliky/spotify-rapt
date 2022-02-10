import base64
import os
from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests


class AuthManager(ABC):
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    AUTH_URL = "https://accounts.spotify.com/authorize"

    @property
    def client_id(self):
        self._client_id = os.getenv("CLIENT_ID")

    @property
    def client_secret(self):
        self._client_secret = os.getenv("CLIENT_SECRET")

    @property
    def redirect_uri(self):
        self._redirect_uri = os.getenv("REDIRECT_URI")

    @abstractproperty
    def grant_type(self):
        pass

    # @abstractmethod
    # def authorise():
    #     pass

    def get_client_credentials(self):
        """
        Returns client credentials, encoded in base64
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id is None or client_secret is None:
            raise Exception("You must set a client ID and a client secret to authorise")
        client_credentials = f"{client_id}:{client_secret}"
        client_credentials_b64 = base64.b64encode(client_credentials.encode())
        return client_credentials_b64.decode()

    def get_auth_headers(self):
        """
        Returns basic authorization credentials
        """
        client_credentials_b64 = self.get_client_credentials()
        return {"Authorization": f"Basic {client_credentials_b64}"}

    def get_auth_response(self):
        """
        Returns authorization response in the form of json data
        """
        auth_url = self.AUTH_URL
        auth_data = self.grant_type  # Could be _, or could be method
        auth_headers = self.get_auth_headers()
        auth_response = requests.post(auth_url, data=auth_data, headers=auth_headers)
        if auth_response.status_code not in range(200, 299):
            raise Exception("Could not authenticate client, please try again")
        return auth_response.json()


class ClientAuth(AuthManager):
    AUTH_URL = "https://accounts.spotify.com/api/token"
    # client_id = None
    # client_secret = None

    @property
    def grant_type(self):
        self._grant_type = {"grant_type": "client_credentials"}

    def __init__(self, client_id, client_secret):
        """
        Initialises the client with the supplied client id and secret
        """
        self.client_id = client_id
        self.client_secret = client_secret

    # def get_client_credentials(self):
    #     """
    #     Returns client credentials, encoded in base64
    #     """
    #     client_id = self.client_id
    #     client_secret = self.client_secret
    #     if client_id is None or client_secret is None:
    #         raise Exception("You must set a client ID and a client secret to authorise")
    #     client_credentials = f"{client_id}:{client_secret}"
    #     client_credentials_b64 = base64.b64encode(client_credentials.encode())
    #     return client_credentials_b64.decode()

    # def get_auth_data(self):
    #     """
    #     Returns authorization body for client credentials flow
    #     """
    #     return {"grant_type": "client_credentials"}

    # def get_auth_headers(self):
    #     """
    #     Returns authorization header for client credentials flow
    #     """
    #     client_credentials_b64 = self.get_client_credentials()
    #     return {"Authorization": f"Basic {client_credentials_b64}"}

    # def get_auth_response(self):
    #     """
    #     Returns authorization response in the form of json data
    #     """
    #     auth_url = self.AUTH_URL
    #     auth_data = self.get_auth_data()
    #     auth_headers = self.get_auth_headers()
    #     auth_response = requests.post(auth_url, data=auth_data, headers=auth_headers)
    #     if auth_response.status_code not in range(200, 299):
    #         raise Exception("Could not authenticate client, please try again")
    #     return auth_response.json()

    def get_access_token(self):
        """
        Returns access token
        """
        return self.get_auth_response()["access_token"]

    def get_token_expires_in(self):
        """
        Returns access token expiry
        """
        return self.get_auth_response()["expires_in"]


class OAuth(AuthManager):

    # TOKEN_URL = "https://accounts.spotify.com/api/token"
    # AUTH_URL = "https://accounts.spotify.com/authorize"
    # client_id = None
    # client_secret = None
    # redirect_uri = None
    # grant_type = None

    @property
    def grant_type(self):
        self._grant_type = {"grant_type": "client_credentials"}

    response_type = "code"
    state = None
    scope = None

    def __init__(self, client_id, client_secret):
        """
        Initialises the client with suplpied client id and secret
        """
        self.client_id = client_id
        self.client_secret = client_secret

    def get_auth_data(self):
        """
        Returns the auth data necessary for the authorisation post request in the authorisation code flow
        """
        return {"grant_type": "authorization_code"}

    def get_auth_url(self, state=None):
        """
        Returns the authorisation URL to be requested
        """
        auth_url = self.AUTH_URL
        client_id = self.client_id
        # client_secret = self.client_secret
        response_type = self.response_type
        redirect_uri = self.redirect_uri
        query = {
            "client_id": client_id,
            "response_type": response_type,
            "redirect_uri": redirect_uri,
        }
        if self.scope:
            query["scope"] = self.scope
        if state is None:
            query["state"] = state
        # OPTIONAL: if instance has show dialog option, add this to the query
        urlparams = urlencode(query)
        return f"{auth_url}?{urlparams}"

    def get_auth_response_interactive(self):
        auth_url = self.get_auth_url()
        webbrowser.open(auth_url)
        pass

    def open_auth_url(self):
        pass

    @staticmethod
    def parse_auth_url(url):
        """
        Parses the given Authorization URL in the Authorization Code Flow,
        returning the state and code in positions 1 and 2 respectively
        """
        query = urlparse(url).query
        form = parse_qs(query)
        if "error" in form:
            raise Exception("Error authorising user")
        return tuple(form.get(param) for param in ["state", "code"])

    def parse_response_code(self, url):
        """
        Parses the response code for the Authorization Code Flow
        """
        _, code = self.parse_auth_url(url)
        if code is None:
            return url
        else:
            return code

    def get_auth_response(self):
        pass

    def get_auth_headers(self):
        pass

    def get_access_token(self, code=None):
        """
        Returns access token
        """
        auth_url = self.AUTH_URL
        query = {
            "redirect_uri": self.redirect_uri,
            "code": code or self.get_auth_response(),
            "grant_type": "authorization_code",
        }
        if self.scope:
            query["scope"] = self.scope
        if self.state:
            query["self"] = self.state

        headers = self.get_auth_headers()
        auth_response = requests.post(auth_url)

    def validate_token(self, token_info):
        pass
