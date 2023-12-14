from app.services import ServicesExtension
from app.models import ModelsExtension
from app.models.profiles import ProfileCreate
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

    def create(self, input: ProfileCreate):
        self.cleanup(input.email)
        time.sleep(2)   # Temporary fix for free plan
        profile = self.models.profiles.create(input)

        return profile, lambda: self.cleanup(profile.email)

    def create_admin(self, input: ProfileCreate):
        profile, cleanup = self.create(input)

        users = self.services.auth0.client.users
        users.add_roles(profile.idp_id, [AUTH0_ROLES[Auth0Role.Admin.value]])

        return profile, cleanup
