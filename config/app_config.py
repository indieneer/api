from .environment import setup_environment
from os import environ as env, path


environment = setup_environment()


def get_fb_service_account():
    """Loads firebase service account from `.credentials/<environment>/firebase` or `.env.<environment>`

    Returns:
        str: service account
    """

    path_to_file = f".credentials/{environment}/firebase"

    if path.isfile(path_to_file):
        with open(path_to_file, "r") as file:
            return file.read()
    else:
        return env.get("FB_SERVICE_ACCOUNT", "")


app_config = {
    "VERSION": env.get("VERSION", "0.0.1"),
    "ENVIRONMENT": environment,
    "PORT": env.get("PORT", 5001),
    "MONGO_URI": env.get("MONGO_URI"),
    "ROOT_USER_EMAIL": env.get("ROOT_USER_EMAIL"),
    "ROOT_USER_PASSWORD": env.get("ROOT_USER_PASSWORD"),
    "FB_NAMESPACE": env.get("FB_NAMESPACE"),
    "FB_SERVICE_ACCOUNT": get_fb_service_account(),
    "FB_API_KEY": env.get("FB_API_KEY")
}
