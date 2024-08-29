import http.client
import json


def get_savan_data():
    conn = http.client.HTTPSConnection("www.jiosaavn.com")

    # Define the endpoint and parameters
    endpoint = "/api.php"
    params = "_format=json&_marker=0&api_version=4&ctx=web6dot0&__call=webapi.getLaunchData"

    # Make the GET request
    conn.request("GET", f"{endpoint}?{params}")

    # Get the response
    response = conn.getresponse()

    # Read and decode the response
    data = response.read().decode()

    # Parse the JSON data
    json_data = json.loads(data)

    return json_data
