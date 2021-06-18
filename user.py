# Zach Marcus
# CS 493, Cloud Application Development
# Final Project
# ================================================================
# This file handles all the routes associated with the user entity.
# ================================================================
from flask import Blueprint, request, jsonify
from google.cloud import datastore
import json
import constants


# Create datastore instance and set up the blueprint for /users.
client = datastore.Client()
bp = Blueprint('user', __name__, url_prefix='/users')


@bp.route('', methods=['GET'])
def users_get():
    """
    Handler for getting all the users.
    """
    query = client.query(kind=constants.USERS)
    results = list(query.fetch())
    final_result_array = []

    for e in results:
        final_result = {"unique_id":"", "nickname":""}
        workable = json.dumps(e)
        workable = json.loads(workable)
        final_result["unique_id"] = workable["unique_id"]
        final_result["nickname"] = workable["nickname"]
        final_result["boats"] = workable["boats"]
        final_result_array.append(final_result)
    return json.dumps(final_result_array)
