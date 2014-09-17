""" 
    test the hmac logic for client and server 
"""
import hmac
from hashlib import sha512
from uuid import uuid4
import json

private_key = str(uuid4())
user_id = str(uuid4())

def send_data():
    """ send the data """
    hmac_hash = hmac.new(private_key, '', sha512)
    ## add some content data
    data = {'a': 1, 'b': 2}
    #print json.dumps((data), indent=4)
    hmac_hash.update(json.dumps((data)))
    return hmac_hash.hexdigest(), data

def recieve_data(pos_hmac_hash, data):
    """ recieve the data """
    hmac_hash = hmac.new(private_key, '', sha512)
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
