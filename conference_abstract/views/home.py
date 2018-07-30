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
This is the home page for brave
"""

service = Service(name='home', path='/', description=info_desc)

@service.get()
def service_get(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
    sql="select * from stats_and_dates order by id desc limit 1"
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql)
    statsAndDates = cur.fetchall()[0]
    conn.close()
    return conference_abstract.util.generate_template('home.mako',{"user":user,"request":request, "statsAndDates":statsAndDates})

