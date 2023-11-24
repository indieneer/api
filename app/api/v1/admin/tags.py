from flask import Blueprint, request, current_app
from validator import rules as R, validate

from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.models.tags import TagCreate, TagPatch
from lib.http_utils import respond_error, respond_success
from app.api.exceptions import UnprocessableEntityException

tags_controller = Blueprint('tags', __name__, url_prefix='/tags')

GENRE_FIELDS = (
    "name"
)


@tags_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_tags():
    """
    Retrieve all tags.

    This endpoint requires authentication and is accessible only to users with an 'admin' role.
    It retrieves all tags from the database.

    :return: A success response with the list of all tags.
    :rtype: dict
    """
    tags_model = get_models(current_app).tags
    tags = [tag.as_json() for tag in tags_model.get_all()]

    return respond_success(tags)


@tags_controller.route('/<string:tag_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_tag_by_id(tag_id):
    """
    Retrieve a specific tag by its ID.

    This endpoint requires authentication and is accessible only to users with an 'admin' role.
    It retrieves the tag corresponding to the given tag_id.

    :param str tag_id: The ID of the tag to be retrieved.
    :raises IndexError: If no tag with the provided ID is found.
    :return: A success response with the details of the requested tag.
    :rtype: dict
    """
    tags_model = get_models(current_app).tags

    try:
        tag_data = tags_model.get(tag_id)

        if tag_data is None:
            raise IndexError(f'The tag with ID {tag_id} was not found.')

        return respond_success(tag_data.as_json())

    except IndexError:
        return respond_error(f'The tag with ID {tag_id} was not found.', 404)


@tags_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_tag():
    """
    Create a new tag.

    This endpoint requires authentication and is accessible only to users with an 'admin' role.
    It creates a new tag with the data provided in the request body.

    :raises: ValueError if the request body does not conform to the required structure or validation rules.
    :return: A success response with the details of the created tag, including its ID.
    :rtype: dict
    """
    tag_data = request.get_json()
    required_fields = {"name": R.Required()}

    # Check for any fields not present in the required fields
    if any(field not in required_fields for field in tag_data.keys()):
        raise UnprocessableEntityException

    # Validate tag data
    validation_result = validate(tag_data, required_fields, return_info=True)
    if isinstance(validation_result, bool):
        if not validation_result:
            raise UnprocessableEntityException
        validated_data = tag_data
    else:
        result, validated_data, errors = validation_result
        if errors:
            raise UnprocessableEntityException(f'Bad Request. {errors}')

    tags_model = get_models(current_app).tags

    created_tag = tags_model.create(TagCreate(validated_data["name"]))

    return respond_success(created_tag.as_json(), status_code=201)


@tags_controller.route('/<string:tag_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_tag(tag_id):
    """
    Update a specific tag by its ID.

    This endpoint requires authentication and is accessible only to users with an 'admin' role.
    It updates the tag corresponding to the given tag_id with the data provided in the request body.
    The update is restricted to certain fields defined in GENRE_FIELDS.

    :param str tag_id: The ID of the tag to be updated.
    :raises ValueError: If the request body contains keys that are not allowed.
    :raises NotFoundException: If no tag with the provided ID is found.
    :return: A success response with the details of the updated tag.
    :rtype: dict
    """
    update_data = request.get_json()

    # Validate keys in update data
    if any(key not in GENRE_FIELDS for key in update_data):
        invalid_keys = [key for key in update_data if key not in GENRE_FIELDS]
        raise UnprocessableEntityException(f'The keys {invalid_keys} are not allowed.')

    tags_model = get_models(current_app).tags

    updated_tag = tags_model.patch(tag_id, TagPatch(name=update_data["name"]))

    if updated_tag is None:
        return respond_error(f'The tag with ID {tag_id} was not found.', 404)

    return respond_success(updated_tag.as_json())


@tags_controller.route('/<string:tag_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_tag(tag_id):
    """
    Delete a specific tag by its ID.

    This endpoint requires authentication and is accessible only to users with an 'admin' role.
    It deletes the tag corresponding to the given tag_id.

    :param str tag_id: The ID of the tag to be deleted.
    :raises NotFoundException: If no tag with the provided ID is found.
    :return: A success response indicating successful deletion of the tag.
    :rtype: dict
    """
    tags_model = get_models(current_app).tags

    deleted_tag = tags_model.delete(tag_id)

    if deleted_tag is None:
        return respond_error(f'The tag with ID {tag_id} was not found.', 404)

    return respond_success(f'Successfully deleted the tag with ID {deleted_tag._id}')
