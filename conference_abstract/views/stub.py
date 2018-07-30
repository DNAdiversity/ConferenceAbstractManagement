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
import time

info_desc = """\
This is the stub page for the dna conference
"""

service = Service(name='stub', path='/stub', description=info_desc)

@service.get()
def service_get(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    if login is not None:
        user = conference_abstract.auth.check_user(request)
    if user == False or user == None:
        headers = pyramid.security.forget(request)
        loc = request.route_url('login')
        return HTTPFound(location=loc)
    templateVars = {
        "user":user,
        "request":request,
        "pageTitle":"",
        "pageDesc":""
    }
    return conference_abstract.util.generate_template('stub.mako',templateVars)

@service.post()
def service_post(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    if login is not None:
        user = conference_abstract.auth.check_user(request)
    if user == False or user == None:
        headers = pyramid.security.forget(request)
        loc = request.route_url('login')
        return HTTPFound(location=loc)
    postObj = {}
    for key in request.POST:
        postObj[key] = request.POST.getall(key)
    
    return conference_abstract.util.generate_response(postObj)
