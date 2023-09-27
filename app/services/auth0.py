from auth0.authentication import GetToken
from auth0.management import Auth0


class ManagementAPI():
    """Used to interact with Auth0 management API
    """

    __client: Auth0
    __token: GetToken

    def __init__(
            self,
            domain: str,
            client_id: str,
            client_secret: str,
            audience: str
    ):
        # todo: handle token expiration
        self.__token = GetToken(domain, client_id, client_secret=client_secret)
        token = self.__token.client_credentials(audience)
        mgmt_api_token = token['access_token']

        self.__client = Auth0(domain, mgmt_api_token)

    @property
    def client(self):
        return self.__client

    @property
    def token(self):
        return self.__token
