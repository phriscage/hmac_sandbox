#!/usr/bin/env python

import os
import sys

sys.path.append('/usr/local/hmac_sandbox/www')

#from impactapi.v1.api.main import app as application
from main import create_app
application = create_app()
