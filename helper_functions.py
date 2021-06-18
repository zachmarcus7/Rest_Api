# Zach Marcus
# CS 493, Cloud Application Development
# Final Project
# ================================================================
# This is file contains all the helper functions for checking the
# data inside the requests made to both the endpoints for boats 
# and loads.
# ================================================================
from flask import Flask, request, Response, jsonify
from flask import make_response, session
import json
import constants


def check_incoming(request):
    """ 
    Ensures incoming request media type is application/json. 
    If the mimetype is anything other than application/json, a
    415 error response will be returned.
    """
    if request.mimetype != "application/json":
        output = {"Error":"Media type must be application/json"}
        response = make_response(jsonify(output))
        response.headers["Accept"] = "application/json"
        response.status_code = 415
        return response
    else:
        return None


def check_outgoing(request):
    """ 
    Ensures outgoing response media type accepted is application/json.
    If the accepted mimetyoe is anything other than application/json, a
    406 error response will be returned.
    """
    if "application/json" not in request.accept_mimetypes:
        output = {"Error":"Accepted media type must be application/json"}
        response = make_response(jsonify(output))
        response.status_code = 406
        return response
    else:
        return None


def check_mimetypes(request):
    """
    Makes sure the incoming and outgoing media type is application/json.
    """
    first = check_incoming(request)
    if first is not None:
        return first

    second = check_outgoing(request)
    if second is not None:
        return second
    return None


def validate_json(request):
    """
    Similar to check_incoming, this checks if the actual body
    of the request is application/json.
    """
    try:
        content = request.get_json()
    except Exception as e:
        output = {"Error":"Media type must be application/json"}
        response = make_response(jsonify(output))
        response.headers["Accept"] = "application/json"
        response.status_code = 415
        return response, "error"
    else:
        return content, "no error"


def validate_name(content):
    """
    Validates the name attribute inside the request.
    """
    if not isinstance(content.get("name"), int):
        upper_case = content.get("name").upper()
        for x in upper_case:
            if ord(x) < 65 or ord(x) > 90:
                return (jsonify({"Error":"Object name must only contain characters"}), 400)
    else:
        return (jsonify({"Error":"Object name must only contain characters"}), 400)

    # check that the name attribute is only 20 characters long
    if len(content.get("name")) > 20:
        return (jsonify({"Error":"Object name can only be 20 characters long"}), 400)
    return None


def validate_type(content):
    """
    Validates the type attribute inside the request.
    """
    if not isinstance(content.get("type"), int):
        upper_case = content.get("type").upper()
        for x in upper_case:
            if ord(x) < 65 or ord(x) > 90:
                return (jsonify({"Error":"Object type must only contain characters"}), 400)
    else:
        return (jsonify({"Error":"Object type must only contain characters"}), 400)

    # check that the type attribute is only 20 characters long
    if len(content.get("type")) > 20:
        return (jsonify({"Error":"Object type can only be 20 characters long"}), 400)
    return None


def validate_length(content):
    """
    Validates the type attribute inside the request.
    """
    if not isinstance(content.get("length"), int):
        return (jsonify({"Error":"Object length must contain only integers"}), 400)
    
    # check that the length attribute is less than 1000
    if content.get("length") > 999:
        return (jsonify({"Error":"Object length must be less than 1000"}), 400)
    return None


def validate_boat_attributes(content):
    """
    Validates all three attributes of the request. Returns None if 
    there are no errors found in the request attributes.
    """

    # check that the request body has all the required attributes
    if content.get("name") is None or content.get("type") is None or content.get("length") is None:
        return (jsonify({"Error":"The request object is missing at least one of the required attributes"}), 400)
    
    first = validate_name(content)
    if first is not None:
        return first

    second = validate_type(content)
    if second is not None:
        return second

    third = validate_length(content)
    if third is not None:
        return third
    return None


def validate_content(content):
    """
    Validates the content attribute inside the request.
    """
    if not isinstance(content.get("content"), int):
        upper_case = content.get("content").upper()
        for x in upper_case:
            if ord(x) < 65 or ord(x) > 90:
                return (jsonify({"Error":"Object content must only contain characters"}), 400)
    else:
        return (jsonify({"Error":"Object content must only contain characters"}), 400)

    # check that the content attribute is only 20 characters long
    if len(content.get("content")) > 20:
        return (jsonify({"Error":"Object content can only be 20 characters long"}), 400)
    return None


def validate_destination(content):
    """
    Validates the destination attribute inside the request.
    """
    if not isinstance(content.get("destination"), int):
        upper_case = content.get("destination").upper()
        for x in upper_case:
            if ord(x) < 65 or ord(x) > 90:
                return (jsonify({"Error":"Object destination must only contain characters"}), 400)
    else:
        return (jsonify({"Error":"Object destination must only contain characters"}), 400)

    # check that the destination attribute is only 20 characters long
    if len(content.get("destination")) > 20:
        return (jsonify({"Error":"Object destination can only be 20 characters long"}), 400)
    return None


def validate_volume(content):
    """
    Validates the volume attribute inside the request.
    """
    if not isinstance(content.get("volume"), int):
        return (jsonify({"Error":"Object volume must contain only integers"}), 400)
    
    # check that the volume attribute is less than 1000
    if content.get("volume") > 999:
        return (jsonify({"Error":"Object volume must be less than 1000"}), 400)
    return None


def validate_load_attributes(content):
    """
    Validates all three attributes of the request. Returns None if 
    there are no errors found in the request attributes.
    """

    # check that the request body has all the required attributes
    if content.get("content") is None or content.get("destination") is None or content.get("volume") is None:
        return (jsonify({"Error":"The request object is missing at least one of the required attributes"}), 400)
    
    first = validate_content(content)
    if first is not None:
        return first

    second = validate_destination(content)
    if second is not None:
        return second

    third = validate_volume(content)
    if third is not None:
        return third
    return None
    