from config import configuration
from auth0.authentication import GetToken
from auth0.management import Auth0


class Auth0API:
    def __init__(self):
        domain = configuration.get("AUTH0_DOMAIN")
        client_id = configuration.get("AUTH0_CLIENT_ID")
        client_secret = configuration.get("AUTH0_CLIENT_SECRET")

        get_token = GetToken(domain, client_id, client_secret=client_secret)
        token = get_token.client_credentials('https://{}/api/v2/'.format(domain))
        mgmt_api_token = token['access_token']

        self._auth0 = Auth0(domain, mgmt_api_token)

    def get_auth0(self):
        return self._auth0

    auth0 = property(get_auth0)
