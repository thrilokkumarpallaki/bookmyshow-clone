from flask import jsonify, make_response


def create_response(resp_json, status=200):
    resp = jsonify(resp_json)
    return make_response(resp, status)
