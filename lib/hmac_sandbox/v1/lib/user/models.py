"""
    user.models.py
"""
from __future__ import absolute_import
import uuid
import time
import re
import logging
from werkzeug import generate_password_hash, check_password_hash

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
        self.valid_args = [self.key_name]
        self._validate_args()
        self.set_key(self.meta, self.kwargs[self.key_name])
        self.current_time = time.time()

    def _validate_args(self):
        """ validate the model args """
        logger.debug("Validating args...")
        if self.key_name not in self.kwargs:
            message = "'%s' is missing." % self.key_name
            raise ValueError(message)
        elif not EMAIL_REGEX.match(self.kwargs[self.key_name]):
            message = "'%s' is not valid." % self.kwargs[self.key_name]
            raise ValueError(message)
        if self.kwargs.get('password'):
            self.set_password(self.kwargs['password'])
        for valid_arg in [self.key_name]:
            if self.kwargs.get(valid_arg):
                self.values[valid_arg] = self.kwargs[valid_arg]
        
    def set_values(self, values=None):
        """ set the model attributes and default values """
        logger.debug("Setting attributes...")
        if not values:
            self.set_group('user')
            self.set_client_api_key('default')
            self.values['created_at'] = self.current_time
        else:
            self.values = values
        
    def _set_client_api_key(self, client_name, idx=None):
        """ set the client api key and secret """
        if not idx:
            idx = 0
        client = {
            'name': client_name,
            'api_key': str(uuid.uuid4()),
            'api_secret': str(uuid.uuid4()),
            'created_at': self.current_time
        }
        self.values['clients'].insert(idx, client)

    def _set_group(self, group_name, idx=None):
        """ set the group """
        if not idx:
            idx = 0
        group = {
            'name': group_name,
            'is_active': True
        }
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
        if override:
            self._set_client_api_key(client_name)
        if not self.values.get('clients'):
            self.values['clients'] = []
            idx = 0
        else:
            idx, client = next(((idx, client) 
                for idx, client in enumerate(self.values['clients'])
                if client_name == client['name']), (None, None))
            if client:
                for key in ['api_key', 'api_secret']:
                    if not client.get(key):
                        logger.warn("'%s' already exists for key: '%s'." % (key,
                            self.key))
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
    user = User(email_address='abc', a=1, password='123')
    print user.values
    print user.check_password('123')
    print user.check_password('1234')
