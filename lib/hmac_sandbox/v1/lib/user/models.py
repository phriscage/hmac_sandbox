"""
    user.models.py
"""
from __future__ import absolute_import
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + 
    '/../../../../../lib')
import time
import re
import logging
from werkzeug import generate_password_hash, check_password_hash
from couchbase.exceptions import KeyExistsError

from hmac_sandbox.v1.lib.client.models import Client

EMAIL_REGEX = re.compile(r'[^@]+@[^@]+\.[^@]+')
REQUIRED_ARGS = ['db_client', 'email_address']
KEY_NAME = 'email_address'

logger = logging.getLogger(__name__)

class User(object):
    """ encapsulate the user as an object """
    
    def __init__(self, **kwargs):
        """ instantiate the class """
        self.key = None
        self.values = {}
        self.children = {}
        self.db_client = None
        self._validate_args(**kwargs)
        self.set_key(self.__class__.__name__.lower(), kwargs[KEY_NAME])
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
        if not EMAIL_REGEX.match(kwargs[KEY_NAME]):
            message = ("'%s' is not valid '%s'." % (kwargs[KEY_NAME], KEY_NAME))
            raise ValueError(message)
        if kwargs.get('password'):
            self.set_password(str(kwargs['password']))

    def _set_client_api_key(self, client_name, idx=None):
        """ set the client api key and secret """
        if idx is None:
            idx = 0
        client = Client(db_client=self.db_client, user_id=self.key)
        client.set_values('default')
        self.children[client.key] = client.values ## saved once object is saved
        if len(self.values['clients']) > 0:
            self.values['clients'].pop(idx)
        self.values['clients'].insert(idx, {
            'client_id': client.key, 
            'name': client_name,
            'created_at': client.values['created_at']
        })

    def _set_group(self, group_name, idx=None):
        """ set the group """
        if idx is None:
            idx = 0
        group = {
            'name': group_name,
            'is_active': True
        }
        if len(self.values['groups']) > 0:
            self.values['groups'].pop(idx)
        self.values['groups'].insert(idx, group)

    def set_key(self, attr, value):
        """ set the key value """
        self.key = '%s::%s' % (attr, value)
        logger.info("'%s' created." % self.key)

    def set_values(self, values=None):
        """ set the model attributes and default values """
        logger.debug("Setting attributes...")
        if not values:
            self.values['created_at'] = self.current_time
            self.set_group('user')
            self.set_client_api_key('default')
        else:
            self.values = values
        
    def set_password(self, password):
        """ set the password using werkzeug generate_password_hash """
        self.values['password'] = generate_password_hash(password)

    def check_password(self, password):
        """ check the password using werkzeug check_password_hash """
        if 'password' not in self.values or not self.values['password']:
            return None
        return check_password_hash(self.values['password'], password)

    def set_client_api_key(self, client_name, override=False):
        """ set the api key and secret for a specific client_name """
        logger.info("Starting...")
        #if override:
            #self._set_client_api_key(client_name)
        if self.values.get('clients') is None:
            self.values['clients'] = []
            idx = 0
        else:
            idx, client = next(((idx, client) 
                for idx, client in enumerate(self.values['clients'])
                if client_name == client['name']), (None, None))
            if not idx is None and not override:
                logger.debug("No existing client and override is False")
                return False
        self._set_client_api_key(client_name, idx)
        logger.info("Finished")
        return True

    def set_group(self, group_name, admin=False):
        """ set the group for a specific group_name """
        logger.info("Starting...")
        if not self.values.get('groups'):
            self.values['groups'] = []
            #idx = 0
        #else:
            #idx, group = next(((idx, group)
                #for idx, group in enumerate(self.values['groups'])
                #if group_name == group['name']), (None, None))
        if admin:
            self._set_group('administrator')
        self._set_group(group_name)
        logger.info("Finished")
        return True

    def add(self):
        """ add the couchbase document and/or children """
        try:
            data = self.db_client.add(self.key, self.values)
            logger.debug("Setting new document(s) for '%s'" % self.children)
            try:
                children_data = self.db_client.set_multi(self.children)
            except Exception as error:
                logger.exception(error)
                raise
        except KeyExistsError as error:
            logger.warn(error)
            raise
        return data

if __name__ == '__main__':
    import json
    args = { 
        'email_address': 'abc@abc.com',
        'db_client': 'abc', 
        'extra': 1,
        'password': '123abc'
    }
    user = User(**args)
    user.set_values()
    print json.dumps(user.values, indent=4)
    #user.set_client_api_key('default', True)
    print user.check_password('123')
    print user.check_password('1234')
