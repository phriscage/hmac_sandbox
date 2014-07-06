"""
    event.models.py
"""
from __future__ import absolute_import
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) +
    '/../../../../../lib')
import uuid
import time
import logging

REQUIRED_ARGS = ['db_client', 'user_id', 'client_id']

logger = logging.getLogger(__name__)

class Event(object):
    """ encapsulate the OpenXC Event as an object """
    
    def __init__(self, **kwargs):
        """ instantiate the class """
        self.key = None
        self.values = {}
        self.db_client = None
        self._validate_args(**kwargs)
        self.set_key(self.__class__.__name__.lower(), str(uuid.uuid4()))
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

    def _set_values(self, data):
        """ set the values """
        self.values['created_at'] = self.current_time
        self.values.update(data)

    def set_key(self, attr, value):
        """ set the key value """
        self.key = '%s::%s' % (attr, value)
        logger.info("'%s' created." % self.key)

    def set_values(self, data):
        """ set the values for a specific event_name """
        logger.info("Starting...")
        if not isinstance(data, dict):
            message = "Not a dictionary: %s" % type(data)
            logger.warn(message)
            raise ValueError(message)
        if data.get('data') is None:
            message = "data attribute must exist: %s" % data
            logger.warn(message)
            raise ValueError(message)
        if len(data['data']) > 5:
            message = "Maximum values is: %s" % len(data['data'])
            logger.warn(message)
            raise ValueError(message)
        self._set_values(data)
        logger.info("Finished")
        return True

    def add(self):
        """ add the couchbase document and/or children """
        try:
            data = self.db_client.add(self.key, self.values)
        except KeyExistsError as error:
            logger.warn(error)
            raise
        return data

if __name__ == '__main__':
    event = Event(db_client='abc', user_id='user::abc@abc.com', 
        client_id='client::b68edfa5-fe9e-47b5-9b56-355fb12d5bac')
    event.set_values({
        "name":"odometer",
        "value":43572.738281,
        "timestamp":1362060000.036000})
    print event.values
