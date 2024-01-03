from dotenv import find_dotenv, load_dotenv

def setup_environment(type: str | None = None):
    if type == "unit":
        return
    
    ENV_FILE = find_dotenv(".env.test")

    if ENV_FILE:
        if not load_dotenv(ENV_FILE):
            print("ERROR: failed to load env!")
        else:
            print("Loaded .env.test!")
    else:
        print("WARNING: env file not found!")
