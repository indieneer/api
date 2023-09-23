from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()

if ENV_FILE:
    if not load_dotenv(ENV_FILE):
        print("ERROR: failed to load env!")
else:
    print("WARNING: env file not found!")
