# Zach Marcus
# CS 493, Cloud Application Development
# Final Project
# ================================================================
# This is file handles all the routes associated with the load entity.
# ================================================================
from flask import Flask, Blueprint, request, Response, jsonify
from flask import make_response, session
from google.cloud import datastore
import json
import constants
import auth0 as auth
import helper_functions as helper
import load_model as mod


# Create datastore instance and set up the blueprint for /loads.
client = datastore.Client()
bp = Blueprint('load', __name__, url_prefix='/loads')


@bp.route('', methods=['POST', 'DELETE', 'PUT', 'PATCH'])
def loads_post():
    """
    Handler for creating a load. A JWT bearer token isn't required.
    """

    # make sure HTTP method is POST
    if request.method == 'PUT' or request.method == 'DELETE' or request.method == 'PATCH':
        output = {"Error":"Method not allowed"}
        response = make_response(jsonify(output))
        response.headers["Accept"] = "POST"
        response.status_code = 405
        return response

    # check incoming and outgoing media types
    mimetype_error = helper.check_mimetypes(request)
    if mimetype_error: return mimetype_error

    # validate request data 
    content, status = helper.validate_json(request)
    validation = helper.validate_load_attributes(content)
    if status != "no error": return content
    if validation: return validation

    # create new load, return its details
    new_load = mod.create_load(content)
    response = mod.get_load(new_load.id, 201, True)
    return response
 

@bp.route('/<id>', methods=['GET'])
def loads_id_get(id):
    """
    Handler for getting a specific load. Doesn't require a JWT.
    """
    # verify that the outgoing mimetype is application/json
    mimetype_error = helper.check_outgoing(request)
    if mimetype_error: return mimetype_error

    # return the boat
    response = mod.get_load(id, 200, False)
    return response


@bp.route('', methods=['GET'])
def loads_get():
    """
    Handler for listing all loads, uses pagination.
    """

    # verify that the outgoing mimetype is application/json
    mimetype_error = helper.check_outgoing(request)
    if mimetype_error: return mimetype_error

    # return details about all the loads
    load_details = mod.get_all_loads()
    return json.dumps(load_details)


@bp.route('/<id>', methods=['DELETE'])
def loads_id_delete(id):
    """
    Handler for deleting a load.
    """
    response = mod.delete_load(id)
    return response


@bp.route('/<id>', methods=['PUT'])
def loads_id_put(id):
    """
    Handler for modifying all properties of a load. Doesn't require
    a JWT.
    """

    # check incoming and outgoing media types
    mimetype_error = helper.check_mimetypes(request)
    if mimetype_error: return mimetype_error

    # validate request data 
    content, status = helper.validate_json(request)
    validation = helper.validate_load_attributes(content)
    if status != "no error": return content
    if validation: return validation

    # return the updated boat
    mod.update_load(content, id, True)
    response = mod.get_load(id, 303, False)
    return response


@bp.route('/<id>', methods=['PATCH'])
def loads_id_patch(id):
    """
    Handler for modifying some properties of a load. No JWT
    required. The only modifiable properties are content, destination, and volume.
    """
    # check incoming and outgoing media types
    mimetype_error = helper.check_mimetypes(request)
    if mimetype_error: return mimetype_error

    # validate request data 
    content, status = helper.validate_json(request)
    if status != "no error": return content

    # make sure there's at least one applicable attribute in the request
    if content.get("content") is None and content.get("destination") is None and content.get("volume") is None:
        return (jsonify({"Error":"The request object is missing at least one of the required attributes"}), 400)

    # validate passed attributes
    if content.get("content") is not None:
        content_error = helper.validate_content(content)
        if content_error: return content_error

    if content.get("destination") is not None:
        destination_error = helper.validate_destination(content)
        if destination_error: return destination_error

    if content.get("volume") is not None:
        volume_error = helper.validate_volume(content)
        if volume_error: return volume_error

    # update the load
    mod.update_load(content, id, False)
    response = mod.get_load(id, 303, False)
    return response
    