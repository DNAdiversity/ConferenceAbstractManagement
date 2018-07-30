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
from conference_abstract.services.data.abstract_info import getAbstract

info_desc = """\
This is the abstract submission success
"""

service = Service(name='abstractSuccess', path='/abstractSuccess/{abstractId}', description=info_desc)


@service.get()
def service_get(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    templateVars = {}
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
        abstractId = request.matchdict['abstractId']
        abstracts, authors = getAbstract(abstractId)
        abstract = None
        abstractAuthors = None
        if abstracts is not None and len(abstracts)>0:
            abstract = abstracts[0]
            abstractAuthors = authors[int(abstractId)]

        return conference_abstract.util.generate_template('abstractSuccess.mako',{
            'user': user,
            'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Abstract Submission"}],
            'abstract':abstract,
            'authors':abstractAuthors,
            'pageTitle':'',
            'pageDesc':''
        })
    return conference_abstract.util.generate_template('error.mako',templateVars)

