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

service = Service(name='loginChair', path='/loginChair', description=info_desc)

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
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
        if user is not None:
            loc = request.route_url('dashboard')
            return HTTPFound(location=loc)

    return conference_abstract.util.generate_template('login.mako',{"user":user,"request":request,"pageTitle":"Chair Login"})

@service.post()
def service_post(request):
    login = pyramid.security.authenticated_userid(request)
    did_fail = False
    user = None
    noAccess = False
    data = {}
    templateVars = {
        'message':'Your email or password is incorrect.<br/> Please try again',
        #'user': user,
        'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Chair Login"}],
        'pageTitle':'Chair Login',
        #'token':token,   # session token
        "request":request
    }
    if 'submit' in request.POST:
        login = request.POST.get('login', '')
        passwd = request.POST.get('passwd', '')
        #user = USERS.get(login, None)
        print login,passwd
        user = User(login,None)

        loginCheck = user.check_password(passwd)
        if user and loginCheck != False:
            # Create session and set cookies
            userObj = user.get_userObj()
            headers = pyramid.security.forget(request)
            conn = conference_abstract.util.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            try:
                sql = """select * from chairs where fk_cusers = %s"""
                sqlOut = cur.mogrify(sql,[userObj["userId"]])
                cur.execute(sql,[userObj["userId"]])
                if cur.rowcount == 1:
                    data = {"sqlran":sqlOut}
                    results = cur.fetchone()
                    accessKey = results["accesskey"]
                    print "*************************************"
                    print "*"
                    print accessKey, sqlOut
                    print "*"
                    print "*************************************"
                    user.get_userObj()
                    userObj = user.get_chairObj(accessKey)
                    headers = pyramid.security.remember(request, login+"|"+str(accessKey)+"|"+str(userObj["chairId"]))
                    print "========== \\/ look here 1 \\/ ========="
                    print login+"|"+str(accessKey)+"|"+str(userObj["chairId"])
                    print "========== /\\ look here /\\ ========="
                    session = request.session
                    session['fullname'] = userObj["fullname"]
                    session['userId'] = userObj["userId"]
                    return HTTPFound(location="/dashboard", headers=headers)
                else:
                    noAccess = True
                    print "========== \/ look here 2 \/ ========="
                    print sqlOut
                    print cur.rowcount
                    print "========== /\ look here /\ ========="
            except Exception as e:
                print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
                print e
                print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        did_fail = True
    user = None
    templateVars['failed_attempt'] = did_fail
    templateVars['login'] = login
    #token = login.split("|")[1] if login is not None else ""
    if noAccess == False:
        return conference_abstract.util.generate_template('login.mako',templateVars)
    else:
        return conference_abstract.util.generate_template('noAccess.mako',{"user":user,"request":request,"pageTitle":"Chair Login"})

