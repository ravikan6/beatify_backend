import http.client
import json
import os
import bcrypt
from base64 import b64decode
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad

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


def decrypt_saavan_media_link(encrypted_media_url: str, quality: str = '320kbps') -> str | None:
    if not encrypted_media_url:
        return None

    qualities = [
        {'id': '_12', 'bitrate': '12kbps'},
        {'id': '_48', 'bitrate': '48kbps'},
        {'id': '_96', 'bitrate': '96kbps'},
        {'id': '_160', 'bitrate': '160kbps'},
        {'id': '_320', 'bitrate': '320kbps'}
    ]

    key = b'38346591'
    iv = b'00000000'  # ECB mode doesn't use IV, but we keep it for clarity.

    # Decode the Base64 encoded encrypted media URL
    encrypted = b64decode(encrypted_media_url)

    # Create a DES cipher in ECB mode
    cipher = DES.new(key, DES.MODE_ECB)

    # Decrypt the data
    decrypted_bytes = cipher.decrypt(encrypted)

    # Remove padding if necessary (assuming PKCS5/PKCS7 padding)
    try:
        decrypted_link = unpad(decrypted_bytes, DES.block_size).decode('utf-8')
    except ValueError:
        decrypted_link = decrypted_bytes.decode('utf-8')

    print(decrypted_link)

    # Return the list of download links with different qualities
    return decrypted_link.replace('_96', qualities[qualities.index(quality)]['id'] if quality in qualities else '_96')


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
