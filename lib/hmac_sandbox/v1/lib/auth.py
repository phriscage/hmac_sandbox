""" 
    auth logic for hmac client and server 
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) +
        '/../../../../lib')

from hmac_sandbox.v1.api.main import db_client

import hmac
import uuid
import json
from hashlib import sha512

private_key = str(uuid.uuid4())

def send_data():
    """ send the data """
    hmac_hash = hmac.new(private_key, '', sha512)
    ## add some content data
    data = {'a': 1, 'b': 2}
    hmac_hash.update(json.dumps((data)))
    return hmac_hash.hexdigest(), data

def verify_client(api_key, hash=None):
    """ verify the client exists """
    key = 'client::%s' % api_key
    client = db_client.get(key, quiet=True)
    if not client.success:
        return {}
    return client
    
def verify_token(private_key, pos_hmac_hash, data, hash_method=None):
    """ recieve the data """
    if not hash_method:
        hash_method = sha512
    hmac_hash = hmac.new(str(private_key), '', hash_method)
    hmac_hash.update(json.dumps((data)))
    if pos_hmac_hash != hmac_hash.hexdigest():
        return False
    return True

def main():
    """ run the main logic """
    hmac_hash, data = send_data()
    print recieve_data(hmac_hash, data)

if __name__ == '__main__':
    main()
