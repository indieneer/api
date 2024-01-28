from app.services import ServicesExtension
from app.models import ModelsExtension
from app.models.profiles import ProfileCreate, ProfileCreateV2
from config.constants import AUTH0_ROLES, Auth0Role
import time


class ProfilesFactory:
    services: ServicesExtension
    models: ModelsExtension

    def __init__(self, services: ServicesExtension, models: ModelsExtension) -> None:
        self.services = services
        self.models = models

    def cleanup(self, email: str):
        users = self.services.auth0.client.users

        search_result = users.list(q=f"email:{email}")
        if len(search_result['users']) != 0:
            user = search_result['users'][0]
            users.delete(user["user_id"])

        db_profile = self.models.profiles.find_by_email(email)
        if db_profile is not None:
            self.models.profiles.delete(str(db_profile._id))

    def create(self, input: ProfileCreateV2):
        self.cleanup(input.email)

        profile = self.models.profiles.create_v2(input)

        return profile, lambda: self.cleanup(profile.email)
