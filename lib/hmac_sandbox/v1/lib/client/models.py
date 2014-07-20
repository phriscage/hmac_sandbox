"""
    client.models.py
"""
from __future__ import absolute_import
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) +
    '/../../../../../lib')
import uuid
import time
import logging

REQUIRED_ARGS = ['db_client', 'user_id']

logger = logging.getLogger(__name__)

class Client(object):
    """ encapsulate the client as an object """
    
    def __init__(self, **kwargs):
        """ instantiate the class """
        self.key = None
        self.values = {}
        self.db_client = None
        self._validate_args(**kwargs)
        self.api_key = str(uuid.uuid4())
        self.set_key(self.__class__.__name__.lower(), self.api_key)
        self.current_time = time.time()

    def _validate_args(self, **kwargs):
        """ validate the model args """
        logger.debug("Validating args...")
        for req_arg in REQUIRED_ARGS:
            if kwargs.get(req_arg) is None:
                message = "'%s' is missing." % req_arg
                logger.warn(message)
                raise ValueError(message)
            if req_arg in ['db_client']:
                setattr(self, req_arg, kwargs.get(req_arg))
            else:
                self.values[req_arg] = kwargs.get(req_arg)

    def _set_api_key(self, client_name):
        """ set the api key and secret """
        self.values.update({
            'name': client_name,
            'api_key': self.api_key,
            'api_secret': str(uuid.uuid4()),
            'created_at': self.current_time,
        })

    def set_key(self, attr, value):
        """ set the key value """
        self.key = '%s::%s' % (attr, value)
        logger.debug("'%s' key created." % self.key)

    def set_values(self, client_name):
        """ set the api key and secret for a specific client_name """
        logger.info("Starting...")
        client_name = str(client_name)
        self._set_api_key(client_name)
        logger.info("Finished")
        return True


if __name__ == '__main__':
    client = Client(db_client='abc', user_id='user::abc@abc.com', a=1)
    client.set_values('default')
    print client.values
