from cornice import Service
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
import pyramid.security

import psycopg2
import psycopg2.extras

import os,sys
import glob
import collections
import datetime

import valideer as V

import conference_abstract.util
import conference_abstract.app_dao
from conference_abstract.auth import User

info_desc = """\
This is the registration page for the dna conference
"""

service = Service(name='loginEditor', path='/loginEditor/{accessKey}', description=info_desc)

def check_user(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    isValid = False
    if login is not None:
        username = login.split("|")[0]
        userId = login.split("|")[1]
        user = User(username)
        isValid = user.is_token_valid(userId)
        print "TESTING FOR SESSION",isValid
    if isValid == False:
        return False
    else:
        session = request.session
        print session
        if 'fullname' in session:
            user.fullname = session["fullname"]
            user.userId = session["userId"]
            user.check_userLevel()
        else:
            userObj = user.get_userObj()
            session['fullname'] = userObj["fullname"]
            session['userId'] = userObj["userId"]
        return user

@service.get()
def service_get(request):
    login = pyramid.security.authenticated_userid(request)
    did_fail = False
    user = None
    data = {}
    accessKey = request.matchdict['accessKey']
    if login is not None:
        headers = pyramid.security.forget(request)
        '''
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
        if user is not None:
            loc = request.route_url('dashboard')
            return HTTPFound(location=loc)
        '''
    try:
        sql = """select * from copyeditors where accesskey = %s"""
        conn = conference_abstract.util.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        sqlOut = cur.mogrify(sql,(accessKey,))
        cur.execute(sql,(accessKey,))
        if cur.rowcount == 1:
            data = {"sqlran":sqlOut}
            results = cur.fetchone()
            user = User('copyeditor@boldsystems.org')
            user.get_userObj()
            userObj = user.get_editorObj(accessKey)
            headers = pyramid.security.remember(request, 'copyeditor@boldsystems.org'+"|"+str(accessKey)+"|"+str(userObj["editorId"]))
            session = request.session
            session['fullname'] = userObj["fullname"]
            session['userId'] = userObj["userId"]
            return HTTPFound(location="/dashboard", headers=headers)
        else:
            print "========== \/ look here \/ ========="
            print sqlOut
            print cur.rowcount
            print "========== /\ look here /\ ========="
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    return conference_abstract.util.generate_template('noAccess.mako',{"user":user,"request":request,"pageTitle":"Login"})

