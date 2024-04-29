from typing import Union

from bson import ObjectId

from app.models import ModelsExtension
from app.models.service_profiles import ServiceProfile, ServiceProfileCreate
from app.services import Database, ServicesExtension


class ServiceProfilesFactory:
    services: ServicesExtension
    models: ModelsExtension

    def __init__(self, models: ModelsExtension, services: ServicesExtension) -> None:
        self.models = models
        self.services = services

    def cleanup(self, profile_id: ObjectId):
        auth = self.services.firebase.auth

        try:
            user = auth.get_user(f"service|{profile_id}")

            auth.delete_user(user.uid)
        except auth.UserNotFoundError:
            # Intentionally skip error if a user does not exist
            pass
        except Exception as error:
            raise error

        db_profile = self.delete_db_profile(str(profile_id))
        if db_profile is not None:
            try:
                self.delete_db_profile(str(db_profile._id))
            except BaseException:
                # Intentionally skip error
                pass

    def create(self, input_data: Union[ServiceProfile, ServiceProfileCreate]):
        if isinstance(input_data, ServiceProfile):
            raise Exception("Not implemented")
        else:
            profile = self.models.service_profiles.create(input_data)

        return profile, lambda: self.cleanup(profile._id)

    def delete_db_profile(self, profile_id: str):
        model = self.models.service_profiles

        model.db.connection[model.collection].find_one_and_delete(
            {"_id": ObjectId(profile_id)},
        )
