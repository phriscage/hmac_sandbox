"""
    user.models.py
"""
from __future__ import absolute_import
import uuid
import time
from werkzeug import generate_password_hash, check_password_hash

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
        self._validate_attrs()
        self._set_attrs()

    def _validate_attrs(self):
        """ validate the model attributes """
        if self.key_name not in self.kwargs:
            message = "'%s' is missing." % self.key_name
            raise ValueError(message)
        elif not self.kwargs[self.key_name]:
            message = "'%s' cannot be blank." % self.key_name
            raise ValueError(message)
        
    def _set_attrs(self):
        """ set the attributes """
        self.set_key(self.meta, self.kwargs[self.key_name])
        if 'password' in self.kwargs:
            self.set_password(self.kwargs['password'])
        self.set_api_key()
        for valid_arg in [self.key_name]:
            if valid_arg in self.kwargs:
                self.values[valid_arg] = self.kwargs[valid_arg]
        self.values['created_at'] = time.time()
        
    def set_key(self, attr, value):
        """ set the key value """
        self.key = '%s::%s' % (attr, value)

    def set_password(self, password):
        """ set the password using werkzeug generate_password_hash """
        self.values['password'] = generate_password_hash(password)

    def check_password(self, password):
        """ check the password using werkzeug check_password_hash """
        if 'password' not in self.values or not self.values['password']:
            return None
        return check_password_hash(self.values['password'], password)

    def set_api_key(self):
        """ set the api key and secret """
        self.values['api_key'] = str(uuid.uuid4())
        self.values['api_secret'] = str(uuid.uuid4())


if __name__ == '__main__':
    user = User(email_address='abc', a=1, password='123')
    print user.values
    print user.check_password('123')
    print user.check_password('1234')
