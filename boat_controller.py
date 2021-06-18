# Zach Marcus
# CS 493, Cloud Application Development
# Final Project
# ================================================================
# This is file handles all the routes associated with the boat entity.
# ================================================================
from flask import Flask, Blueprint, request, Response, jsonify
from flask import make_response, session
from google.cloud import datastore
import json
import constants
import auth0 as auth
import boat_model as mod
import helper_functions as helper


# Create datastore instance and set up the blueprint for /boats.
client = datastore.Client()
bp = Blueprint('boat', __name__, url_prefix='/boats')


@bp.route('', methods=['POST', 'DELETE', 'PUT', 'PATCH'])
def boats_post():
    """
    Handler for creating a boat. Requires a JWT bearer token.
    """

    # verify that the JWT is valid
    if request.headers.get("Authorization") is None:
        return (jsonify({"Error":"JWT is invalid"}), 401)

    payload = auth.verify_jwt(request)
    if payload == "error":
        return (jsonify({"Error":"JWT is invalid"}), 401)

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
    validation = helper.validate_boat_attributes(content)
    if status != "no error": return content
    if validation: return validation

    # create new boat, return its details
    new_boat = mod.create_boat(content, payload)
    response = mod.get_boat(new_boat.id, payload, 201, True)
    return response


@bp.route('/<id>', methods=['GET'])
def boats_id_get(id):
    """
    Handler for getting a specific boat. Requires a JWT.
    """
    
    # verify that the JWT is valid
    if request.headers.get("Authorization") is None:
        return (jsonify({"Error":"JWT is invalid"}), 401)

    payload = auth.verify_jwt(request)
    if payload == "error":
        return (jsonify({"Error":"JWT is invalid"}), 401)

    # verify that the outgoing mimetype is application/json
    mimetype_error = helper.check_outgoing(request)
    if mimetype_error: return mimetype_error

    # return the boat
    response = mod.get_boat(id, payload, 200, False)
    return response
    

@bp.route('', methods=['GET'])
def boats_get():
    """
    Handler for listing all boats, uses pagination. Only shows
    the boats that belong to the owner of the JWT.
    """

    # verify that the JWT is valid
    if request.headers.get("Authorization") is None:
        return (jsonify({"Error":"JWT is invalid"}), 401)

    payload = auth.verify_jwt(request)
    if payload == "error":
        return (jsonify({"Error":"JWT is invalid"}), 401)

    # verify that the outgoing mimetype is application/json
    mimetype_error = helper.check_outgoing(request)
    if mimetype_error: return mimetype_error

    # return details about all the boats
    boat_details = mod.get_all_boats(payload)
    return json.dumps(boat_details)


@bp.route('/<id>', methods=['DELETE'])
def boats_id_delete(id):
    """
    Handler for deleting a boat. Requires a valid JWT.
    """

    # verify that the JWT is valid
    if request.headers.get("Authorization") is None:
        return (jsonify({"Error":"JWT is invalid"}), 401)

    payload = auth.verify_jwt(request)
    if payload == "error":
        return (jsonify({"Error":"JWT is invalid"}), 401)
    
    response = mod.delete_boat(payload, id)
    return response

    
@bp.route('/<id>', methods=['PUT'])
def boats_id_put(id):
    """
    Handler for modifying all properties of a boat. Requires a 
    valid JWT. The only modifiable properties are name, type, and length.
    """

    # verify that the JWT is valid
    if request.headers.get("Authorization") is None:
        return (jsonify({"Error":"JWT is invalid"}), 401)

    payload = auth.verify_jwt(request)
    if payload == "error":
        return (jsonify({"Error":"JWT is invalid"}), 401)

    # check incoming and outgoing media types
    mimetype_error = helper.check_mimetypes(request)
    if mimetype_error: return mimetype_error

    # validate request data 
    content, status = helper.validate_json(request)
    validation = helper.validate_boat_attributes(content)
    user_error = mod.validate_boat_owner(payload, id)
    if status != "no error": return content
    if validation: return validation
    if user_error: return user_error

    # return the updated boat
    mod.update_boat(content, id, True)
    response = mod.get_boat(id, payload, 303, False)
    return response


@bp.route('/<id>', methods=['PATCH'])
def boats_id_patch(id):
    """
    Handler for modifying some properties of a boat. Requires a 
    valid JWT. The only modifiable properties are name, type, and length.
    """

    # verify that the JWT is valid
    if request.headers.get("Authorization") is None:
        return (jsonify({"Error":"JWT is invalid"}), 401)

    payload = auth.verify_jwt(request)
    if payload == "error":
        return (jsonify({"Error":"JWT is invalid"}), 401)

    # check incoming and outgoing media types
    mimetype_error = helper.check_mimetypes(request)
    content, status = helper.validate_json(request)
    if mimetype_error: return mimetype_error
    if status != "no error": return content

    # make sure there's at least one applicable attribute in the request
    if content.get("name") is None and content.get("type") is None and content.get("length") is None:
        return (jsonify({"Error":"The request object is missing at least one of the required attributes"}), 400)

    # validate passed attributes
    if content.get("name") is not None:
        name_error = helper.validate_name(content)
        if name_error: return name_error

    if content.get("type") is not None:
        type_error = helper.validate_type(content)
        if type_error: return type_error

    if content.get("length") is not None:
        length_error = helper.validate_length(content)
        if length_error: return length_error

    # check if the user id matches the owner id of boat
    user_error = mod.validate_boat_owner(payload, id)
    if user_error: return user_error

    # update the boat
    mod.update_boat(content, id, False)
    response = mod.get_boat(id, payload, 303, False)
    return response


@bp.route('/<id>/loads/<lid>', methods=['PUT'])
def boats_id_loads_lid_put(id, lid):
    """
    Handler for placing a load onto a boat. Requires a JWT.
    """

    # verify that the JWT is valid
    if request.headers.get("Authorization") is None:
        return (jsonify({"Error":"JWT is invalid"}), 401)

    payload = auth.verify_jwt(request)
    if payload == "error":
        return (jsonify({"Error":"JWT is invalid"}), 401)

    # check if the user id matches the owner id of boat
    user_error = helper.validate_boat_owner(payload, id)
    if user_error: return user_error

    response = mod.add_load(payload, id, lid)
    return response

    
@bp.route('/<id>/loads/<lid>', methods=['DELETE'])
def boats_id_loads_lid_delete(id, lid):
    """
    Handler for removing a load from a boat. Requires a JWT.
    """

    # verify that the JWT is valid
    if request.headers.get("Authorization") is None:
        return (jsonify({"Error":"JWT is invalid"}), 401)

    payload = auth.verify_jwt(request)
    if payload == "error":
        return (jsonify({"Error":"JWT is invalid"}), 401)

    # check if the user id matches the owner id of boat
    user_error = helper.validate_boat_owner(payload, id)
    if user_error: return user_error
        
    response = mod.remove_load(payload, id, lid)
    return response