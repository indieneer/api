from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from tools.http_utils import respond_success, respond_error
from bson.json_util import dumps, loads
import os

app = Flask(__name__)
client = MongoClient(timeoutMS=500)
__version__ = "0.0.1"
env = os.environ.get("PYTHON_ENV")


@app.route('/')
def index():
    return 'Hello, Flask!'


@app.route('/v1/health')
def health():
    try:
        mongodb_status = client.indineer.command("ping")
        health_obj = {
            "db": mongodb_status,
            "env": env,
            "version": __version__
        }
        return respond_success(health_obj)
    except ServerSelectionTimeoutError as e:
        health_obj = {
            "db": str(e),
            "env": env,
            "version": __version__
        }
        return respond_success(health_obj)
    except Exception as e:
        return respond_error(f'{str(e)}', 500)


@app.route('/v1/products', methods=["GET"])
def get_products():
    fetched = [
        {
            "_id": "jsfdjksdfjksdf",
            "name": "Fortnite",
        },

        {
            "_id": "fsdjsjfdsdf",
            "name": "Mainokrafto",
        }
    ]

    return respond_success(fetched)
    # TODO: implement real functionality


@app.route('/v1/profiles', methods=["POST"])
def create_profile():
    db = client["indieneer"]
    profiles = db["profiles"]

    data = request.get_json()

    new_profile = {
        "email": data.get("email"),
        "password": data.get("password"),
    }

    result = profiles.insert_one(new_profile)
    new_profile["_id"] = str(new_profile["_id"]) # I hate this line

    return respond_success(new_profile, None, 201)


if __name__ == '__main__':
    app.run(debug=True)
