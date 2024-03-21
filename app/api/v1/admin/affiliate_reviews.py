from flask import Blueprint, request, current_app
from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.models.affiliate_reviews import AffiliateReviewPatch, AffiliateReviewCreate
from lib.http_utils import respond_success, respond_error

affiliate_reviews_controller = Blueprint('affiliate_reviews', __name__, url_prefix='/affiliate_reviews')

AFFILIATE_REVIEW_FIELDS = [
    "user",
    "affiliate_platform_product_id",
    "text",
    "rating"
]


@affiliate_reviews_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_affiliate_reviews():
    """
    Retrieve all affiliate reviews.

    This endpoint returns a list of all affiliate reviews from the database.
    Requires authentication and admin privileges.
    """
    affiliate_reviews_model = get_models(current_app).affiliate_reviews
    affiliate_reviews_list = affiliate_reviews_model.get_all()
    return respond_success([review.to_json() for review in affiliate_reviews_list])


@affiliate_reviews_controller.route('/<string:review_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_affiliate_review(review_id):
    """
    Retrieve a single affiliate review by ID.

    This endpoint returns the details of a specific affiliate review.
    Requires authentication and admin privileges.
    """
    affiliate_reviews_model = get_models(current_app).affiliate_reviews
    review = affiliate_reviews_model.get(review_id)
    if review:
        return respond_success(review.to_json())
    else:
        return respond_error(f'Affiliate review with ID {review_id} not found', 404)


@affiliate_reviews_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_affiliate_review():
    """
    Create a new affiliate review.

    This endpoint creates a new affiliate review with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()

    if not data or not all(key in data for key in AFFILIATE_REVIEW_FIELDS):
        return respond_error("Invalid data provided.", 400)
    if not 1 <= data.get("rating", 0) <= 5:
        return respond_error("Rating must be between 1 and 5.", 400)

    review_data = AffiliateReviewCreate(**data)
    affiliate_reviews_model = get_models(current_app).affiliate_reviews
    new_review = affiliate_reviews_model.create(review_data)
    return respond_success(new_review.to_json(), status_code=201)


@affiliate_reviews_controller.route('/<string:review_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_affiliate_review(review_id):
    """
    Update an existing affiliate review.

    This endpoint updates an affiliate review's details with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()

    if "rating" in data and not 1 <= data.get("rating", 0) <= 5:
        return respond_error("Rating must be between 1 and 5.", 400)

    review_patch_data = AffiliateReviewPatch(**data)
    affiliate_reviews_model = get_models(current_app).affiliate_reviews
    updated_review = affiliate_reviews_model.patch(review_id, review_patch_data)
    if updated_review:
        return respond_success(updated_review.to_json())
    else:
        return respond_error(f'Affiliate review with ID {review_id} not found', 404)


@affiliate_reviews_controller.route('/<string:review_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_affiliate_review(review_id):
    """
    Delete an affiliate review by ID.

    This endpoint removes an affiliate review from the database.
    Requires authentication and admin privileges.
    """
    affiliate_reviews_model = get_models(current_app).affiliate_reviews
    deleted_review = affiliate_reviews_model.delete(review_id)
    if deleted_review:
        return respond_success({'message': f'Affiliate review {review_id} successfully deleted'})
    else:
        return respond_error(f'Affiliate review with ID {review_id} not found', 404)
