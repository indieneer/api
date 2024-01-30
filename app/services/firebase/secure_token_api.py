import urllib3

from .user import FirebaseRefreshedToken


class SecureTokenAPI:
    _base_url: str
    _api_key: str

    def __init__(self, api_key: str) -> None:
        self._base_url = "https://securetoken.googleapis.com"
        self._api_key = api_key

    def exchange_refresh_token(self, refresh_token: str):
        # https://firebase.google.com/docs/reference/rest/auth#section-sign-in-email-password

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        response = urllib3.request(
            "POST", f"{self._base_url}/v1/token?key={self._api_key}",
            json=payload
        )

        return FirebaseRefreshedToken(response.json())

    # TODO: refresh token
    # https://firebase.google.com/docs/reference/rest/auth#section-refresh-token
