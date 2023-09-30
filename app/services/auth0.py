from auth0.authentication import GetToken
from auth0.management import Auth0


class ManagementAPI():
    """Used to interact with Auth0 management API
    """

    __client: Auth0 | None = None
    __auth0_token: GetToken | None = None

    __domain: str
    __client_id: str
    __client_secret: str
    __audience: str

    def __init__(
            self,
            domain: str,
            client_id: str,
            client_secret: str,
            audience: str
    ):
        self.__domain = domain
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__audience = audience

    def __refresh_token(self):
        return GetToken(
            self.__domain,
            self.__client_id,
            client_secret=self.__client_secret
        )

    def __create_client(self):
        # TODO: handle token expiration
        mgmt_token = self.auth0_token.client_credentials(self.__audience)
        mgmt_access_token = mgmt_token['access_token']

        return Auth0(self.__domain, mgmt_access_token)

    @property
    def client(self):
        # Lazy initialization
        if self.__client is None:
            self.__client = self.__create_client()

        return self.__client

    @property
    def auth0_token(self):
        # TODO: handle token expiration
        if self.__auth0_token is None:
            self.__auth0_token = self.__refresh_token()

        return self.__auth0_token
