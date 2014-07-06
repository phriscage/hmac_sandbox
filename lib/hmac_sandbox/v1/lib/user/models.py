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

from hmac_sandbox.v1.lib.client.models import Client

EMAIL_REGEX = re.compile(r'[^@]+@[^@]+\.[^@]+')

logger = logging.getLogger(__name__)

class User(object):
    """ encapsulate the user as an object """
    
    def __init__(self, **kwargs):
        """ instantiate the class """
        self.kwargs = kwargs
        self.meta = self.__class__.__name__.lower()
        self.key = None
        self.values = {}
        self.key_name = 'email_address'
        self.required_args = [self.key_name, 'db_client']
        self._validate_args()
        self.set_key(self.meta, self.kwargs[self.key_name])
        self.current_time = time.time()

    def _validate_args(self):
        """ validate the model args """
        logger.debug("Validating args...")
        for req_arg in self.required_args:
            if self.kwargs.get(req_arg) is None:
                message = "'%s' is missing." % req_arg
                logger.warn(message)
                raise ValueError(message)
            #self.values[req_arg] = self.kwargs[req_arg]
        if not EMAIL_REGEX.match(self.kwargs[self.key_name]):
            message = ("'%s' is not valid '%s'." 
                % (self.kwargs[self.key_name], self.key_name))
            raise ValueError(message)
        
    def set_values(self, values=None):
        """ set the model attributes and default values """
        logger.debug("Setting attributes...")
        if not values:
            if self.kwargs.get('password'):
                self.set_password(self.kwargs['password'])
            self.set_group('user')
            self.set_client_api_key('default')
            self.values['created_at'] = self.current_time
            self.values['email_address'] = self.kwargs[self.key_name]
        else:
            self.values = values
        
    def _set_client_api_key(self, client_name, idx=None):
        """ set the client api key and secret """
        if idx is None:
            idx = 0
        client = Client(db_client=self.kwargs['db_client'], user_id=self.key)
        client.set_api_key('default')
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


if __name__ == '__main__':
    import json
    user = User(email_address='abc@abc.com', db_client='abc', a=1, password='123')
    user.set_values()
    print json.dumps(user.values, indent=4)
    #user.set_client_api_key('default', True)
    print user.check_password('123')
    print user.check_password('1234')
