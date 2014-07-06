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

logger = logging.getLogger(__name__)

class Client(object):
    """ encapsulate the client as an object """
    
    def __init__(self, **kwargs):
        """ instantiate the class """
        self.kwargs = kwargs
        self.meta = self.__class__.__name__.lower()
        self.key = None
        self.values = {}
        self.required_args = ['db_client', 'user_id']
        self._validate_args()
        self.api_key = str(uuid.uuid4())
        self.set_key(self.meta, self.api_key)
        self.current_time = time.time()

    def _validate_args(self):
        """ validate the model args """
        logger.debug("Validating args...")
        for req_arg in self.required_args:
            if self.kwargs.get(req_arg) is None:
                message = "'%s' is missing." % req_arg
                logger.warn(message)
                raise ValueError(message)
        
    def _set_api_key(self, client_name):
        """ set the api key and secret """
        self.values = {
            'name': client_name,
            'api_key': self.api_key,
            'api_secret': str(uuid.uuid4()),
            'created_at': self.current_time,
            'user_id': self.kwargs['user_id']
        }

    def set_key(self, attr, value):
        """ set the key value """
        self.key = '%s::%s' % (attr, value)
        logger.info("'%s' created." % self.key)

    def set_api_key(self, client_name):
        """ set the api key and secret for a specific client_name """
        logger.info("Starting...")
        self._set_api_key(client_name)
        logger.info("Finished")
        return True


if __name__ == '__main__':
    client = Client(db_client='abc', user_id='user::abc@abc.com', a=1)
    client.set_api_key('default')
    print client.values
