from cornice import Service
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
import pyramid.security

import psycopg2
import psycopg2.extras

import os
import glob
import collections
import datetime

import valideer as V

import conference_abstract.util
import conference_abstract.app_dao
from conference_abstract.auth import User

info_desc = """\
This is the error page for abstracts the template can be called from any view but this is to be able to work on it without generating an error
"""

service = Service(name='error', path='/error', description=info_desc)

@service.get()
def service_get(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
    return conference_abstract.util.generate_template('error.mako',{"user":user,"request":request})

