import urllib3

from .user import FirebaseUser, FirebaseUserIdentity


class IdentityToolkitAPI:
    _base_url: str
    _api_key: str

    def __init__(self, api_key: str) -> None:
        self._base_url = "https://identitytoolkit.googleapis.com"
        self._api_key = api_key

    def sign_in(self, email: str, password: str):
        # https://firebase.google.com/docs/reference/rest/auth#section-sign-in-email-password

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = urllib3.request(
            "POST", f"{self._base_url}/v1/accounts:signInWithPassword?key={self._api_key}",
            json=payload
        )

        return FirebaseUserIdentity(response.json())

    def lookup(self, idToken: str):
        # https://firebase.google.com/docs/reference/rest/auth#section-get-account-info

        payload = {
            "idToken": idToken
        }

        response = urllib3.request(
            "POST", f"{self._base_url}/v1/accounts:lookup?key={self._api_key}",
            json=payload
        )

        data = response.json()
        users = data.get("users", [])

        if len(users) == 0:
            raise Exception("User not found.")

        return FirebaseUser(users[0])
