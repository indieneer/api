from os import environ as env

from dotenv import find_dotenv, load_dotenv


def setup_environment():
    environment = env.get("ENVIRONMENT", "development")

    if environment == "test":
        return environment

    ENV_FILE = find_dotenv(".env")

    if ENV_FILE:
        if load_dotenv(ENV_FILE):
            print(f"Loaded env from \"{ENV_FILE}\"")
        else:
            print("ERROR: failed to load env!")
    else:
        print("WARNING: env file not found!")

    return environment
