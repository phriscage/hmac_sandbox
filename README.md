hmac_sandbox
=====================

A Python Flask API for hash message authentication code (HMAC) framework utilizing Couchbase's distributed document store. Private and client keys are generated from a basic user registration form interface.

Diretory Structure
-------------------------

The application folder structure is defined below:

    lib/
        <object>/
            v1/
                <resource>/
            v2/
                <resource>/
    www/
        templates/
            <object>/
        static/
            <object>/

Quick Start
-------------------------

Execute ./www/main.py to launch the UI.

    $ ./www/main.py --port 8080
    * Running on http://0.0.0.0:8080/
    * Restarting with reloader

Execute ./lib/hmac_sandbox/v1/api/main.py to launch the API.

    $ ./lib/hmac_sandbox/v1/api/main.py
    * Running on http://0.0.0.0:8000/
    * Restarting with reloader
