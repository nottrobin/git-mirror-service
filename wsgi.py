#!/usr/bin/env python

# System
import os
import urlparse
import subprocess

# Modules
from wsgiref.simple_server import make_server

# Globals
script_dir = os.path.dirname(os.path.realpath(__file__))
secret_filename = os.path.join(script_dir, ".secret")


def get_param(query_string, param_name):
    """
    Get the first param value from a query string
    or return None
    """

    params = urlparse.parse_qs(query_string)

    if param_name in params:
        return params[param_name][0]


def application(environ, start_response):
    """
    An application for a WSGI interface
    """

    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    output = ""

    secret = get_param(environ['QUERY_STRING'], 'secret')
    origin = get_param(environ['QUERY_STRING'], 'origin')
    destination = get_param(environ['QUERY_STRING'], 'destination')

    real_secret = None

    if os.path.isfile(secret_filename):
        with open(secret_filename) as secret_file:
            real_secret = secret_file.read().strip()

    if (real_secret and not secret) or not origin or not destination:
        status = '400 Bad Request'
        output = "Missing one of `secret`, `origin` or `destination`"
    elif secret and secret != real_secret:
        status = '401 Unauthorized'
        output = "Invalid secret token"
    else:
        copy_command = (
            '{script_dir}/copy-repository.py {origin} {destination}'
        ).format(
            script_dir=script_dir,
            origin=origin,
            destination=destination
        )

        output = subprocess.check_output(
            copy_command.split(),
            stderr=subprocess.STDOUT
        )

    start_response(status, headers)

    return [output]


if __name__ == "__main__":
    httpd = make_server('', 9052, application)
    print "Serving on port 9052..."
    httpd.serve_forever()
