from auth0.authentication import GetToken
from auth0.management import Auth0
from auth0.exceptions import Auth0Error
from os import environ as env

from config import configuration
from services.database import Database as dbs

ADMIN_ROLE_ID = "rol_BW5opLbZAHM9BGr8"


def create_root_profile():
    try:
        db = dbs.client.get_default_database()
        profiles = db["profiles"]

        admin_profile = {
            "email": configuration["ROOT_USER_EMAIL"],
            "password": configuration["ROOT_USER_PASSWORD"]
        }

        # should be abstracted
        email = admin_profile["email"]
        password = admin_profile["password"]

        domain = env.get("AUTH0_DOMAIN")
        client_id = env.get("AUTH0_CLIENT_ID")
        client_secret = env.get("AUTH0_CLIENT_SECRET")

        get_token = GetToken(domain, client_id, client_secret=client_secret)
        token = get_token.client_credentials('https://{}/api/v2/'.format(domain))
        mgmt_api_token = token['access_token']

        auth0 = Auth0(domain, mgmt_api_token)

        user = auth0.users.create({"email": email, "password": password, "email_verified": True,
                                   "connection": "Username-Password-Authentication"})

        idp_id = user["identities"][0]["user_id"]
        auth0.users.add_roles("auth0|" + idp_id, [ADMIN_ROLE_ID])

        admin_profile["idp_id"] = idp_id
        profiles.insert_one(admin_profile)

        admin_profile["_id"] = str(admin_profile["_id"])

        auth0.users.update(f'auth0|{idp_id}', {"user_metadata": {"profile_id": admin_profile["_id"]}})

        print(f'Root user {configuration["ROOT_USER_EMAIL"]} successfully created!')

    except Auth0Error as e:
        print(f'Root user {configuration["ROOT_USER_EMAIL"]} already exists')
    except Exception as e:
        print(str(e))


create_root_profile()
