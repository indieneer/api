from app.services import ServicesExtension
from app.models import ModelsExtension
from app.models.profiles import ProfileCreate


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
                self.models.profiles.delete_db_profile(str(db_profile._id))
            except:
                # Intentionally skip error
                pass

    def create(self, input: ProfileCreate):
        self.cleanup(input.email)

        profile = self.models.profiles.create(input)

        return profile, lambda: self.cleanup(profile.email)
