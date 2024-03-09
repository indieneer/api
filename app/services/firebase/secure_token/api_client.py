import urllib3

from .dto import FirebaseRefreshedToken
from .http import ExchangeRefreshTokenRequest


class SecureTokenAPI:
    _base_url: str
    _api_key: str

    def __init__(self, api_key: str) -> None:
        self._base_url = "https://securetoken.googleapis.com"
        self._api_key = api_key

    # https://firebase.google.com/docs/reference/rest/auth#section-refresh-token
    def exchange_refresh_token(self, refresh_token: str):
        response = urllib3.request(
            "POST",
            f"{self._base_url}/v1/token?key={self._api_key}",
            json=ExchangeRefreshTokenRequest("refresh_token", refresh_token=refresh_token).to_json()
        )

        return FirebaseRefreshedToken(response.json())
