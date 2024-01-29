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
        auth = self.services.firebase.auth

        try:
            user = auth.get_user_by_email(email)

            auth.delete_user(user.uid)
        except auth.UserNotFoundError:
            # Intentionally skip error if a user does not exist
            pass
        except Exception as error:
            raise error

        db_profile = self.models.profiles.find_by_email(email)
        if db_profile is not None:
            try:
                self.models.profiles.delete_v2(str(db_profile._id))
            except auth.UserNotFoundError:
                # Intentionally skip error if a user does not exist
                pass

    def create(self, input: ProfileCreateV2):
        self.cleanup(input.email)

        profile = self.models.profiles.create_v2(input)

        return profile, lambda: self.cleanup(profile.email)
