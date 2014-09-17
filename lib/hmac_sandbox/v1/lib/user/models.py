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
VALID_ARGS = ['first_name', 'last_name']
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
        for valid_arg in VALID_ARGS:
            if kwargs.get(valid_arg) is not None:
                self.values[valid_arg] = kwargs.get(valid_arg)

    def _set_client(self, client_name):
        """ set the client api key and secret """
        client = Client(db_client=self.db_client, user_id=self.key)
        client.set_values(client_name)
        self.children[client.key] = client.values ## saved once object is saved
        self.values['clients'][client_name] = {
            'client_id': client.key, 
            'created_at': client.values['created_at']
        }

    def _set_group(self, group_name):
        """ set the group """
        if group_name not in self.values['groups']:
            self.values['groups'].insert(0, group_name)

    def set_key(self, attr, value):
        """ set the key value """
        self.key = '%s::%s' % (attr, value)
        logger.debug("'%s' key set." % self.key)

    def set_values(self, values=None):
        """ set the model attributes and default values """
        logger.debug("Setting attributes...")
        if not values:
            self.values['created_at'] = self.current_time
            self.set_group('user')
            self.set_client('default')
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

    def is_authenticated(self):
        """ should just return True unless the object represents a user
            that should not be allowed to authenticate for some reason.
        """
        return True

    def is_active(self):
        """ method should return True for users unless they are inactive, for
            example because they have been banned.
        """
        return True

    def is_anonymous(self):
        """ method should return True only for fake users that are not supposed
            to log in to the system.
        """
        return False

    def set_client(self, client_name, override=False):
        """ set the api key and secret for a specific client_name """
        logger.info("Setting the client_name: '%s'" % client_name)
        #if override:
            #self._set_client(client_name)
        if self.values.get('clients') is None:
            self.values['clients'] = {}
        else:
            if self.values['clients'].get(client_name) is not None \
            and not override:
                logger.debug("No existing client and override is False")
                return False
        self._set_client(client_name)
        return True

    def set_group(self, group_name, admin=False):
        """ set the group for a specific group_name """
        logger.info("Setting the group_name: '%s'" % group_name)
        if not self.values.get('groups'):
            self.values['groups'] = []
        if admin:
            self._set_group('administrator')
        self._set_group(group_name)
        return True

    def get_id(self):
        """ return the self.key """
        return self.values[KEY_NAME]

    def add(self):
        """ add the couchbase document and/or children """
        logger.info("Adding the document for key: '%s'" % self.key)
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
    #user.set_client('default', True)
    print user.check_password('123')
    print user.check_password('1234')
