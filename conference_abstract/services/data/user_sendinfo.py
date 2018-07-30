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
import unicodedata

import conference_abstract.util
import conference_abstract.app_dao
from conference_abstract.auth import User
import time

info_desc = """\
This will check if an email already exists
"""

service = Service(name='sendInfo', path='/users/{userId}/sendinfo',description=info_desc)

@service.get()
def data_get(request):
    #allowed = pyramid.security.authenticated_userid(request)
    #if allowed is None:
    #    raise HTTPForbidden()

    data = {
        'success': True,
    }
    params = request.GET
    userId = str(request.matchdict['userId'])

    try:
        conn = conference_abstract.util.get_connection()
        #cur = conn.cursor()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = """SELECT first_name, last_name, institution, email, password from cusers where id=%s;"""
        print cur.mogrify(sql,[userId])
        cur.execute(sql,[userId])
        if cur.rowcount == 1:
            results = cur.fetchone()
            message = """
Dear %s,

This is an automated email regarding your new account on the Conference Abstract system for the 2017 International Barcode of Life Conference.  

Please use this account to submit abstracts for consideration.

You may now log into the Conference Abstract system
http://abstracts.dnabarcodes2017.org/login

Please use the following to login:
email: %s
password: %s

Thank you, from the Conference Operating Committee
            """
            print "firstname"
            firstname = unicodedata.normalize('NFKD', results["first_name"].decode("utf-8")).encode('ascii', 'ignore')
            print "lastname"
            lastname = unicodedata.normalize('NFKD', results["last_name"].decode("utf-8")).encode('ascii', 'ignore')
            print "inst"
            institution = unicodedata.normalize('NFKD', results["institution"].decode("utf-8")).encode('ascii', 'ignore')
            print "email"
            email = unicodedata.normalize('NFKD', results["email"].decode("utf-8")).encode('ascii', 'ignore')
            print "pass"
            password = results["password"]
            print "sending"
            conference_abstract.util.sendMail("abstracts@ibol.org",[email],"Conference Abstract Account",message % (firstname + ' ' + lastname, email, password))
            print "sent"
        else:
            data["success"] = False
    except Exception as e:
        print 'bang!', e
        data['success'] = 'Error'
        data['message'] = 'Could not retrieve records'
        return conference_abstract.util.generate_response(data)

    return conference_abstract.util.generate_response(data)
