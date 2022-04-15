from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, \
    HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import User, db
from flasgger import swag_from
from flask import Blueprint, request
import os
import json
from pprint import pprint
import requests
public_1 = Blueprint('public_1', __name__, url_prefix="/api/v1/data/public_1")


@public_1.route('/')
@jwt_required()
def handle_public_1():
    query_table = request.args.get('query_table')
    db_engine = db.create_engine(os.environ.get("SQLALCHEMY_DB_URI"), {})
    current_user = get_jwt_identity()
    # user = current_user.query.filter_by(id=current_user).first()
    user = User.query.filter_by(id=current_user).first()

    current_zuhubh = user.zuhubh
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    # bookmarks = Bookmark.query.filter_by(
    #     user_id=current_user).paginate(page=page, per_page=per_page)
    with db_engine.connect() as conn:
        db_engine.execute("USE basdata")
        result = db_engine.execute(f"select * from basdata.{query_table} where zuhubh = {current_zuhubh}")

    result_ult = jsonify({'result': [dict(row) for row in result]})

    return result_ult, HTTP_200_OK


