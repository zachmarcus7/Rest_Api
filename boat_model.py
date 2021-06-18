# Zach Marcus
# CS 493, Cloud Application Development
# Final Project
# ================================================================
# This is file handles all the interaction with google datastore for
# the boat entity.
# ================================================================
from flask import Flask, request, Response, jsonify
from flask import make_response, session
from google.cloud import datastore
import json
import constants


# Create datastore instance 
client = datastore.Client()


def create_boat(content, payload):
    """
    Creates a new boat in datastore.
    """
    new_boat = datastore.entity.Entity(key=client.key(constants.BOATS))
    new_boat.update({"name": content["name"], "type": content["type"], "length": content["length"],
                     "loads": [], "owner": payload["sub"]})
    client.put(new_boat)
    update_user(payload, new_boat)
    return new_boat


def update_user(payload, new_boat):
    """
    Updates user entity in datastore.
    """
    query = client.query(kind=constants.USERS)
    results = list(query.fetch())
    for e in results:
        workable = json.dumps(e)
        workable = json.loads(workable)
        if workable["unique_id"] == payload["sub"]:
            # update the boat
            user_key = client.key(constants.USERS, int(e.key.id))
            user = client.get(key=user_key)
            user["boats"].append({"id":new_boat.id, "self": str(request.url) + "/" + str(new_boat.id)})
            client.put(user)


def get_boat(id, payload, status, new):
    """
    Retrieves info from datastore for specified boat. If the boat belongs to another owner,
    or if the boat doesn't currently exist in the datastore, then an error response gets returned.
    If new is True, then the self attribute will be automatically generated with the new id, else
    the request url will be set as the self attribute.
    """
    query = client.query(kind=constants.BOATS)
    results = list(query.fetch())
    final_result = {"id":"", "name":"", "type": "", "length":"", "loads":[], "owner":"", "self":""}

    for e in results:
        if e.key.id == int(id):
            workable = json.dumps(e)
            workable = json.loads(workable)

            # check if the user id matches the owner id of boat
            if workable["owner"] != payload["sub"]:
                return (jsonify({"Error":"Not authorized"}), 403)

            final_result["id"] = str(e.key.id)
            final_result["name"] = workable["name"]
            final_result["type"] = workable["type"]
            final_result["length"] = workable["length"]
            final_result["loads"] = workable["loads"]
            final_result["owner"] = workable["owner"]

            # check if this is a new boat, set the self attribute based on this
            if new:
                final_result["self"] = str(request.url) + "/" + str(e.key.id) 
            else:
                final_result["self"] = str(request.url)

            response = make_response(jsonify(final_result))
            response.headers["Content-Type"] = "application/json"

            # check if the location header needs to be set
            if status == 303:
                response.headers["Location"] = str(request.url)

            response.status_code = status
            return response
    return (jsonify({"Error":"No boat with this boat_id exists"}), 404)


def get_all_boats(payload):
    """
    Retrieves info from datastore for all boats that match the sub
    property in the supplied JWT. Uses pagination.
    """
    # get the total number of boats
    boat_count = 0
    query = client.query(kind=constants.BOATS)
    q_limit = int(request.args.get('limit', '5'))
    q_offset = int(request.args.get('offset', '0'))
    l_iterator = query.fetch(limit= q_limit, offset=q_offset)
    pages = l_iterator.pages
    results = list(next(pages))

    if l_iterator.next_page_token:
        next_offset = q_offset + q_limit
        next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
    else:
        next_url = None

    # only return boats that belong to the sub property of the JWT
    final_result_array = []
    for e in results:
        workable = json.dumps(e)
        workable = json.loads(workable)
        if workable["owner"] != payload["sub"]:
            continue
        final_result = {"id":"", "name":"", "type": "", "length":"", "loads":[], "owner":"", "self":""}
        final_result["id"] = str(e.key.id)
        final_result["name"] = workable["name"]
        final_result["type"] = workable["type"]
        final_result["length"] = workable["length"]
        final_result["loads"] = workable["loads"]
        final_result["owner"] = workable["owner"]
        final_result["self"] = str(request.url) + "/" + str(e.key.id)
        final_result_array.append(final_result)
    output = {"boats": final_result_array}
    output["total_items"] = boat_count
    if next_url:
        output["next"] = next_url
    return output


def delete_boat(payload, id):
    """
    Deletes a specific boat from the datastore and updates 
    any connected loads.
    """
    boat_key = client.key(constants.BOATS, int(id))
    boat = client.get(key=boat_key)

    # check if boat exists
    if boat is None:
        return (jsonify({"Error":"No boat with this boat_id exists"}), 404)
    
    # check if the user id matches the owner id of boat
    if boat["owner"] != payload["sub"]:
        return (jsonify({"Error":"Not authorized"}), 403)

    # update user entity
    query = client.query(kind=constants.USERS)
    results = list(query.fetch())
    for e in results:
        workable = json.dumps(e)
        workable = json.loads(workable)
        if workable["unique_id"] == boat["owner"]:
            user_key = client.key(constants.USERS, int(e.key.id))
            user = client.get(key=user_key)
            old_boats = user["boats"]
            user["boats"] = []

            for current_boat in old_boats:
                if int(current_boat["id"]) != e.key.id:
                    user["boats"].append(current_boat) 
            client.put(user)

    # remove all loads from boat
    for i in boat["loads"]:
        workable = json.dumps(i)
        workable = json.loads(workable)
        load_key = client.key(constants.LOADS, int(workable["id"]))
        load = client.get(key=load_key)

        load["carrier"] = "none"
        client.put(load)

    client.delete(boat_key)
    return ("", 204)


def validate_boat_owner(payload, id):
    """
    Checks if the user id matches the owner id of boat.
    """
    boat_key = client.key(constants.BOATS, int(id))
    boat = client.get(key=boat_key)

    if boat["owner"] != payload["sub"]:
        return (jsonify({"Error":"Not authorized"}), 403)
    return None


def update_boat(content, id, whole):
    """
    Updates the specified boat. If whole is true, then the entire boat
    gets updated, else only the passed attributes get updated.
    """
    if whole:
        boat_key = client.key(constants.BOATS, int(id))
        boat = client.get(key=boat_key)
        boat.update({"name":content.get("name"), "type": content.get("type"), "length":content.get("length")})
        client.put(boat)
    else:
        boat_key = client.key(constants.BOATS, int(id))
        boat = client.get(key=boat_key)
        if content.get("name") is not None:
            boat.update({"name":content.get("name")})
        if content.get("type") is not None:
            boat.update({"type":content.get("type")})
        if content.get("length") is not None:
            boat.update({"length":content.get("length")})
        client.put(boat)


def add_load(payload, id, lid):    
    """
    Adds specified load to boat.
    """
    # check if the boat and load exist
    boat_key = client.key(constants.BOATS, int(id))
    boat = client.get(key=boat_key)
    load_key = client.key(constants.LOADS, int(lid))
    load = client.get(key=load_key)

    if boat is None:
        return (jsonify({"Error":"No boat with this boat_id exists"}), 404)

    if load is None:
        return (jsonify({"Error":"No load with this load_id exists"}), 404)
        
    b_workable = json.dumps(boat)
    b_workable = json.loads(b_workable)
    l_workable = json.dumps(load)
    l_workable = json.loads(l_workable)

    if l_workable is None or b_workable is None:
        return (jsonify({"Error":"The specified boat and/or load does not exist"}), 404)

    # check that the load isn't already assigned to another boat
    if l_workable["carrier"] == "none":
        # update the load
        carrier_info = {"self": request.host_url + "boats/" + id, "name": b_workable["name"], "id": id}
        load.update({"carrier": carrier_info})
        client.put(load)

        # update the boat
        load_info = {"id": lid, "self": request.host_url + "loads/" + lid}
        all_loads = boat["loads"]
        all_loads.append(load_info)
        boat.update({"loads": all_loads})
        client.put(boat)

        return('', 204)
    else:
        return(jsonify({"Error":"The specified load already has a carrier"}), 403)
    

def remove_load(payload, id, lid):
    """
    Removes specified load from boat.
    """
    # check if the boat and load exist
    boat_key = client.key(constants.BOATS, int(id))
    boat = client.get(key=boat_key)
    load_key = client.key(constants.LOADS, int(lid))
    load = client.get(key=load_key)

    if boat is None:
        return (jsonify({"Error":"No boat with this boat_id exists"}), 404)

    if load is None:
        return (jsonify({"Error":"No load with this load_id exists"}), 404)

    b_workable = json.dumps(boat)
    b_workable = json.loads(b_workable)
    l_workable = json.dumps(load)
    l_workable = json.loads(l_workable)

    if l_workable is None or b_workable is None:
        return (jsonify({"Error":"The specified boat and/or load does not exist"}), 404)

    # check that the load isn't already assigned to another boat
    if l_workable["carrier"] == "none":
        return(jsonify({"Error":"The specified load is not on this carrier"}), 403)
    elif l_workable["carrier"]["id"] != id:
        return(jsonify({"Error":"The specified load is not on this carrier"}), 403)
    else:
        # update load
        load.update({"carrier": "none"})
        client.put(load)
        
        # update boat
        new_loads = []
        for current_load in boat["loads"]:
            if current_load["id"] != lid:
                new_loads.append(current_load)
        boat["loads"] = new_loads
        client.put(boat)
        return('', 204)
