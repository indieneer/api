import firebase_admin.auth

from app.models import ModelsExtension
from app.models.profiles import ProfileCreate
from config import app_config
from config.constants import FirebaseRole


def run(models: ModelsExtension):
    """Creates a root admin profile for future management

    Args:
        services (ServicesExtension): services
    """
    try:
        profile = models.profiles.find_by_email(app_config["ROOT_USER_EMAIL"])

        if profile is not None:
            raise Exception("Skipping root user creation")

        profile = models.profiles.create(ProfileCreate(
            email=app_config["ROOT_USER_EMAIL"],
            nickname="indieneer",
            password=app_config["ROOT_USER_PASSWORD"],
            display_name="Admin",
            email_verified=True,
            role=FirebaseRole.Admin
        ))

        if profile is None:
            raise Exception("user is missing in the database")

        print(f"Root profile created: {profile._id}")
    except firebase_admin.auth.EmailAlreadyExistsError as error:
        print(f"Skipping root user creation: {error}")
    except Exception as e:
        print(f"Failed to create root user: {e}")
