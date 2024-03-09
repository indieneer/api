import urllib3

from .dto import FirebaseCustomIdentity, FirebaseUser, FirebaseUserIdentity
from .exceptions import NotFoundException
from .http import (LookupRequest, LookupResponse, SignInWithCustomTokenRequest,
                   SignInWithPasswordRequest, inflate_response)


class IdentityToolkitApiClient:
    _base_url: str
    _api_key: str

    def __init__(self, api_key: str) -> None:
        self._base_url = "https://identitytoolkit.googleapis.com"
        self._api_key = api_key

    # https://firebase.google.com/docs/reference/rest/auth#section-sign-in-email-password
    def sign_in(self, email: str, password: str):
        raw_response = urllib3.request(
            "POST",
            f"{self._base_url}/v1/accounts:signInWithPassword?key={self._api_key}",
            json=SignInWithPasswordRequest(email, password).to_json()
        )
        response = inflate_response(raw_response, FirebaseUserIdentity)
        if isinstance(response, Exception):
            raise response

        return response

    # https://firebase.google.com/docs/reference/rest/auth#section-verify-custom-token
    def sign_in_with_custom_token(self, token: str):
        raw_response = urllib3.request(
            "POST",
            f"{self._base_url}/v1/accounts:signInWithCustomToken?key={self._api_key}",
            json=SignInWithCustomTokenRequest(token).to_json()
        )
        response = inflate_response(raw_response, FirebaseCustomIdentity)
        if isinstance(response, Exception):
            raise response

        return response

    # https://firebase.google.com/docs/reference/rest/auth#section-get-account-info
    def lookup(self, id_token: str):
        raw_response = urllib3.request(
            "POST",
            f"{self._base_url}/v1/accounts:lookup?key={self._api_key}",
            json=LookupRequest(id_token).to_json()
        )
        response = inflate_response(raw_response, LookupResponse)
        if isinstance(response, Exception):
            raise response

        if len(response.users) == 0:
            raise NotFoundException(FirebaseUser.__name__)

        return response.users[0]
