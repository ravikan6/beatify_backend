import http.client
import json
import os
import bcrypt

def get_savan_data(params: str = "_format=json&_marker=0&api_version=4&ctx=web6dot0&__call=webapi.getLaunchData"):
    conn = http.client.HTTPSConnection("www.jiosaavn.com")

    # Define the endpoint and parameters
    endpoint = "/api.php"
    params = params

    # Make the GET request
    conn.request("GET", f"{endpoint}?{params}")

    # Get the response
    response = conn.getresponse()

    # Read and decode the response
    data = response.read().decode()

    # Parse the JSON data
    json_data = json.loads(data)

    return json_data


def password_hasher(password: str) -> str:
    salt = bcrypt.gensalt()
    pass_bytes = password.encode('utf-8')
    _hash = bcrypt.hashpw(pass_bytes, salt) 
    return _hash

def password_checker(password: str, hashed_password: str) -> bool:
    try:
        x = bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        return x
    except:
        return False
