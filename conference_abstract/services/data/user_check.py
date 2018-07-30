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
This will check if an email already exists
"""

service = Service(name='verifyPojectCode', path='/users/{email}',description=info_desc)

@service.get()
def data_get(request):
    #allowed = pyramid.security.authenticated_userid(request)
    #if allowed is None:
    #    raise HTTPForbidden()

    data = {
        'success': True,
    }
    params = request.GET
    email = request.matchdict['email']

    try:
        conn = conference_abstract.util.get_connection()
        cur = conn.cursor()
        #TODO: ACL on the records
        sql = "SELECT count(*) from cusers where email=%s;"
        cur.execute(sql,(email,))

        found = cur.fetchone()[0]
        conn.commit()
        if found == 0:
            data["success"] = False
    except Exception as e:
        print 'bang!', e
        data['success'] = 'Error'
        data['message'] = 'Could not retrieve records'
        return conference_abstract.util.generate_response(data)

    return conference_abstract.util.generate_response(data)
