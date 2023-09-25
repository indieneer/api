from auth0.exceptions import Auth0Error

from app.services import ServicesExtension
from config import app_config
from config.constants import (
    AUTH0_ROLES,
    Auth0Role
)


def run(services: ServicesExtension):
    """Creates a root admin profile for future management

    Args:
        services (ServicesExtension): services
    """

    try:
        auth0_mgmt = services.auth0.client
        profiles = services.db.connection["profiles"]

        user = services.auth0.client.users.create({
            "email": app_config["ROOT_USER_EMAIL"],
            "password": app_config["ROOT_USER_PASSWORD"],
            "email_verified": True,
            "connection": "Username-Password-Authentication"
        })

        roles = [AUTH0_ROLES[Auth0Role.Admin.value]]
        auth0_mgmt.users.add_roles(user["user_id"], roles)

        # todo: delegate profile creation to profile model
        admin_profile = {
            "email": user["email"],
            "idpId": user["idp_id"],
        }
        profiles.insert_one(admin_profile)

        # update user's metadata in auth0 with internal
        # profile id in order to later easily verify
        # user identity
        auth0_mgmt.users.update(user["user_id"], {
            "user_metadata": {
                "profile_id": str(admin_profile["_id"])
            }
        })

        print(f'Root profile created.')
    except Auth0Error as e:
        if e.status_code == 409:
            print('Skipping root profile creation.')
        else:
            print(f"ERROR: {str(e)}")
    except Exception as e:
        print(f"ERROR: {str(e)}")
