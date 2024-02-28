from bson import ObjectId

from app.models import ModelsExtension
from app.models.profiles import ProfileCreate
from app.services import ServicesExtension


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
                self.delete_db_profile(str(db_profile._id))
            except BaseException:
                # Intentionally skip error
                pass

    def create(self, input: ProfileCreate):
        self.cleanup(input.email)

        profile = self.models.profiles.create(input)

        return profile, lambda: self.cleanup(profile.email)

    def delete_db_profile(self, profile_id: str):
        model = self.models.profiles

        model.db.connection[model.collection].find_one_and_delete(
            {"_id": ObjectId(profile_id)},
        )
