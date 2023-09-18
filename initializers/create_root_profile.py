from services import auth0
from auth0.exceptions import Auth0Error

from config import configuration, AUTH0_ROLES
from services.database import Database as dbs


def create_root_profile():
    try:
        db = dbs.client.get_default_database()
        profiles = db["profiles"]

        admin_profile = {
            "email": configuration["ROOT_USER_EMAIL"],
            "password": configuration["ROOT_USER_PASSWORD"]
        }

        email = admin_profile["email"]
        password = admin_profile["password"]

        user = auth0.users.create({"email": email, "password": password, "email_verified": True,
                                   "connection": "Username-Password-Authentication"})

        idp_id = user["identities"][0]["user_id"]
        auth0.users.add_roles(f"auth0|{idp_id}", [AUTH0_ROLES["Admin"]])  # it is important to pass roles as list

        admin_profile["idp_id"] = idp_id
        profiles.insert_one(admin_profile)

        admin_profile["_id"] = str(admin_profile["_id"])

        auth0.users.update(f'auth0|{idp_id}', {"user_metadata": {"profile_id": admin_profile["_id"]}})

        print(f'Root user {configuration["ROOT_USER_EMAIL"]} successfully created!')

    except Auth0Error as e:
        print(f"Creating Root User: {str(e)}")
    except Exception as e:
        print(str(e))
