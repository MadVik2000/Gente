"""
This file contains all the helpers for spotify app.
"""

from os import environ

import requests

from spotify.exceptions import SpotifyException
from spotify.models import SpotifyAccessToken


def generate_access_token():
    """
    This helper is used to generate a new access token for spotify web API
    """

    url = f'{environ.get("SPOTIFY_ACCOUNTS_BASE_URL")}/token/'
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": environ.get("SPOTIFY_CLIENT_ID"),
        "client_secret": environ.get("SPOTIFY_CLIENT_SECRET"),
        "grant_type": "client_credentials",
    }

    response = requests.post(url=url, headers=headers, data=data)
    if not response.status_code == 200:
        raise SpotifyException(message=response.errors)

    data = response.json()
    spotify_access_token = SpotifyAccessToken(access_token=data["access_token"])
    spotify_access_token.save()
