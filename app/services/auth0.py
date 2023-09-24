from auth0.authentication import GetToken
from auth0.management import Auth0


class ManagementAPI():
    """Used to interact with Auth0 management API
    """

    __client: Auth0

    def __init__(
            self,
            domain: str,
            client_id: str,
            client_secret: str,
            audience: str
    ):
        # todo: handle token expiration
        get_token = GetToken(domain, client_id, client_secret=client_secret)
        token = get_token.client_credentials(audience)
        mgmt_api_token = token['access_token']

        self.__client = Auth0(domain, mgmt_api_token)

    @property
    def client(self):
        return self.__client
