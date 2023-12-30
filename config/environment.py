from os import environ as env

from dotenv import find_dotenv, load_dotenv

def setup_environment():
    TEST = env.get("PYTHON_ENV", "development") == "test"

    # Load env conditionally
    ENV_FILE = find_dotenv(f'.env{".test" if TEST else ""}')

    if ENV_FILE:
        if not load_dotenv(ENV_FILE):
            print("ERROR: failed to load env!")
    else:
        print("WARNING: env file not found!")
