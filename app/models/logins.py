from typing import cast

from app.models.profiles import ProfilesModel
from app.models.service_profiles import ServiceProfilesModel
from app.services.firebase import Firebase, identity_toolkit
from config import app_config
from config.constants import FirebaseRole
from lib.db_utils import Serializable


class AuthenticatedUser(Serializable):
    def __init__(self, identity: identity_toolkit.FirebaseUserIdentity, user: identity_toolkit.FirebaseUser) -> None:
        self.identity = identity
        self.user = user


class LoginsModel:
    profiles: ProfilesModel
    service_profiles: ServiceProfilesModel

    firebase: Firebase
    collection: str = "profiles"

    def __init__(self, firebase: Firebase, profiles: ProfilesModel, service_profiles: ServiceProfilesModel) -> None:
        self.firebase = firebase
        self.profiles = profiles
        self.service_profiles = service_profiles

    def login(self, email: str, password: str):
        identity = self.firebase.identity_api.sign_in(email, password)
        claims = self.firebase.auth.verify_id_token(identity.id_token, clock_skew_seconds=10)

        # TODO: improve data integrity validation before letting users sign in
        profile_id = claims.get(f"{app_config['FB_NAMESPACE']}/profile_id")
        profile = self.profiles.get(profile_id)
        if profile is None:
            return

        return identity

    def login_m2m(self, client_id: str, client_secret: str):
        profile = self.service_profiles.get_by_client_id(client_id)
        if profile is None:
            return

        if profile.client_secret != client_secret:
            return

        claims = {}
        claims[f"{app_config['FB_NAMESPACE']}/roles"] = [FirebaseRole.Service.value]
        claims[f"{app_config['FB_NAMESPACE']}/client_id"] = profile.client_id
        claims[f"{app_config['FB_NAMESPACE']}/profile_id"] = str(profile._id)
        claims[f"{app_config['FB_NAMESPACE']}/permissions"] = profile.permissions

        buffer = cast(bytes, self.firebase.auth.create_custom_token(
            profile.idp_id,
            claims
        ))
        token = buffer.decode('utf-8', 'strict')

        return self.firebase.identity_api.sign_in_with_custom_token(token)

    def exchange_refresh_token(self, refresh_token: str):
        token = self.firebase.secure_token_api.exchange_refresh_token(
            refresh_token
        )

        return token
