from os import environ as env

from dotenv import find_dotenv, load_dotenv

def setup_environment():
    if env.get("PYTHON_ENV", "development") == "test":
        return

    ENV_FILE = find_dotenv(".env")

    if ENV_FILE:
        if not load_dotenv(ENV_FILE):
            print("ERROR: failed to load env!")
    else:
        print("WARNING: env file not found!")
