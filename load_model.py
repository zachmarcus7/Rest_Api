# Zach Marcus
# CS 493, Cloud Application Development
# Final Project
# ================================================================
# This is file handles all the interaction with google datastore for
# the load entity.
# ================================================================
from flask import Flask, request, Response, jsonify
from flask import make_response, session
from google.cloud import datastore
import json
import constants


# Create datastore instance
client = datastore.Client()


def create_load(content):
    """
    Creates a new load in datastore.
    """
    new_load = datastore.entity.Entity(key=client.key(constants.LOADS))
    new_load.update({"content": content["content"], "destination": content["destination"],
                     "volume": content["volume"], "carrier": "none"})
    client.put(new_load)
    return new_load


def get_load(id, status, new):
    """
    Retrieves info from datastore for specified load. If new is True, then the self 
    attribute will be automatically generated with the new id, else the request url 
    will be set as the self attribute.
    """
    query = client.query(kind=constants.LOADS)
    results = list(query.fetch())
    final_result = {"id": "", "content": "", "destination": "", "volume": "", "carrier": "","self": ""}

    for e in results:
        if e.key.id == int(id):
            workable = json.dumps(e)
            workable = json.loads(workable)
            final_result["id"] = str(e.key.id)
            final_result["content"] = workable["content"]
            final_result["destination"] = workable["destination"]
            final_result["volume"] = workable["volume"]
            final_result["carrier"] = workable["carrier"]

            # check if this is a new load, set the self attribute based on this
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
    return (jsonify({"Error":"No load with this load_id exists"}), 404)


def get_all_loads():
    """
    Retrieves info from the datastore about all the loads. 
    """
    # get the total number of loads
    load_count = 0
    query = client.query(kind=constants.LOADS)
    results = list(query.fetch())
    for e in results:
        load_count += 1

    query = client.query(kind=constants.LOADS)
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

    final_result_array = []

    for e in results:
        workable = json.dumps(e)
        workable = json.loads(workable)
        final_result = {"id":"", "content":"", "destination": "", "volume":"", "carrier":"", "self":""}
        final_result["id"] = str(e.key.id)
        final_result["content"] = workable["content"]
        final_result["destination"] = workable["destination"]
        final_result["volume"] = workable["volume"]
        final_result["carrier"] = workable["carrier"]
        final_result["self"] = str(request.url) + "/" + str(e.key.id)
        final_result_array.append(final_result)
    output = {"loads": final_result_array}
    output["total_items"] = load_count
    if next_url:
        output["next"] = next_url
    return output


def delete_load(id):
    """
    Deletes a specific load from the datastore and updates 
    any connected boats.
    """
    query = client.query(kind=constants.LOADS)
    results = list(query.fetch())

    for e in results:
        if e.key.id == int(id):
            workable = json.dumps(e)
            workable = json.loads(workable)

            # check if load is currently on a boat
            if workable["carrier"] != "none":
                carrier_id = int(workable["carrier"]["id"])
                boat_key = client.key(constants.BOATS, carrier_id)
                boat = client.get(key=boat_key)

                # update boat
                old_boat = boat["loads"]
                boat["loads"] = []

                for current_load in old_boat:
                    if int(current_load["id"]) != e.key.id:
                        boat["loads"].append(current_load) 

                client.put(boat)
                client.delete(e.key)
                return('', 204)
            else:
                client.delete(e.key)
                return('', 204)

    return (jsonify({"Error":"No load with this load_id exists"}), 404)


def update_load(content, id, whole):
    """
    Updates the specified load. If whole is true, then the entire load
    gets updated, else only the passed attributes get updated.
    """
    if whole:
        load_key = client.key(constants.LOADS, int(id))
        load = client.get(key=load_key)
        load.update({"content":content.get("content"), "destination": content.get("destination"), "volume":content.get("volume")})
        client.put(load)
    else:
        load_key = client.key(constants.LOADS, int(id))
        load = client.get(key=load_key)

        if content.get("content") is not None:
            load.update({"content":content.get("content")})
        if content.get("destination") is not None:
            load.update({"destination":content.get("destination")})
        if content.get("volume") is not None:
            load.update({"volume":content.get("volume")})
        client.put(load)
