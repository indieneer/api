from bson import ObjectId
from flask import Blueprint, request, current_app
from pymongo import ReturnDocument
from validator import rules as R, validate

from app.middlewares import requires_auth, requires_role
from app.services import get_services
from lib.http_utils import respond_error, respond_success

genres_controller = Blueprint('genres', __name__, url_prefix='/genres')

GENRE_FIELDS = (
    "name"
)


@genres_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_genres():
    """
    Retrieve all genres.

    This endpoint requires authentication and is accessible only to users with an 'admin' role.
    It retrieves all genres from the database.

    :return: A success response with the list of all genres.
    :rtype: dict
    """
    database = get_services(current_app).db.connection
    genres = database.tags.find({})

    formatted_genres = [dict(genre, _id=str(genre["_id"])) for genre in genres]

    return respond_success(formatted_genres)


@genres_controller.route('/<string:tag_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_genre_by_id(tag_id):
    """
    Retrieve a specific genre by its ID.

    This endpoint requires authentication and is accessible only to users with an 'admin' role.
    It retrieves the genre corresponding to the given tag_id.

    :param str tag_id: The ID of the genre to be retrieved.
    :raises IndexError: If no genre with the provided ID is found.
    :return: A success response with the details of the requested genre.
    :rtype: dict
    """
    database = get_services(current_app).db.connection

    try:
        genre_data = next(database.tags.aggregate([
            {'$match': {'_id': ObjectId(tag_id)}}
        ]), None)

        if genre_data is None:
            raise IndexError(f'The genre with ID {tag_id} was not found.')

        genre_data["_id"] = str(genre_data["_id"])

        return respond_success(genre_data)

    except IndexError:
        return respond_error(f'The genre with ID {tag_id} was not found.', 404)


@genres_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_genre():
    """
    Create a new genre.

    This endpoint requires authentication and is accessible only to users with an 'admin' role.
    It creates a new genre with the data provided in the request body.

    :raises: ValueError if the request body does not conform to the required structure or validation rules.
    :return: A success response with the details of the created genre, including its ID.
    :rtype: dict
    """
    genre_data = request.get_json()
    required_fields = {"name": R.Required()}

    # Check for any fields not present in the required fields
    if any(field not in required_fields for field in genre_data.keys()):
        return respond_error('Bad request.', 400)

    # Validate genre data
    validation_result = validate(genre_data, required_fields, return_info=True)
    if isinstance(validation_result, bool):
        if not validation_result:
            return respond_error('Bad request.', 400)
        validated_data = genre_data
    else:
        result, validated_data, errors = validation_result
        if errors:
            return respond_error(f'Bad request. {errors}', 400)

    database = get_services(current_app).db.connection

    database.tags.insert_one(validated_data)

    validated_data["_id"] = str(validated_data["_id"])

    return respond_success(validated_data)


@genres_controller.route('/<string:tag_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_genre(tag_id):
    """
    Update a specific genre by its ID.

    This endpoint requires authentication and is accessible only to users with an 'admin' role.
    It updates the genre corresponding to the given tag_id with the data provided in the request body.
    The update is restricted to certain fields defined in GENRE_FIELDS.

    :param str tag_id: The ID of the genre to be updated.
    :raises ValueError: If the request body contains keys that are not allowed.
    :raises NotFoundException: If no genre with the provided ID is found.
    :return: A success response with the details of the updated genre.
    :rtype: dict
    """
    update_data = request.get_json()

    # Validate keys in update data
    if any(key not in GENRE_FIELDS for key in update_data):
        invalid_keys = [key for key in update_data if key not in GENRE_FIELDS]
        return respond_error(f'The keys {invalid_keys} are not allowed.', 422)

    filter_criteria = {"_id": ObjectId(tag_id)}
    database = get_services(current_app).db.connection

    updated_genre = database["tags"].find_one_and_update(
        filter_criteria, {"$set": update_data}, return_document=ReturnDocument.AFTER)

    if updated_genre is None:
        return respond_error(f'The genre with ID {tag_id} was not found.', 404)

    updated_genre["_id"] = str(updated_genre["_id"])

    return respond_success(updated_genre)


@genres_controller.route('/<string:tag_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_genre(tag_id):
    """
    Delete a specific genre by its ID.

    This endpoint requires authentication and is accessible only to users with an 'admin' role.
    It deletes the genre corresponding to the given tag_id.

    :param str tag_id: The ID of the genre to be deleted.
    :raises NotFoundException: If no genre with the provided ID is found.
    :return: A success response indicating successful deletion of the genre.
    :rtype: dict
    """
    filter_criteria = {"_id": ObjectId(tag_id)}
    database = get_services(current_app).db.connection

    deleted_genre = database["tags"].find_one_and_delete(filter_criteria)

    if deleted_genre is None:
        return respond_error(f'The genre with ID {tag_id} was not found.', 404)

    return respond_success([f'Successfully deleted the genre with ID {deleted_genre["_id"]}'])
