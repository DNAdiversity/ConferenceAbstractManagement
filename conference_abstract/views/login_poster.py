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
This is the Login page for the dna conference after the items have been accepted as posters or talks
"""

service = Service(name='loginPoster', path='/loginPoster', description=info_desc)

def checkValidUser(user):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = """select * from (select distinct(fk_submitter) from 
        (select fk_submitter
        from abstracts 
        where abstract_type in ('Poster') and review_status = 'EDITED' group by fk_submitter) as test
        union
        (select fk_submitter from agenda 
        left join abstracts on agenda.fk_abstracts = abstracts.id
        where abstracts.abstract_type = 'Lightning Talk'
        group by fk_submitter) ) as valid_users
where fk_submitter=%s;"""
    print cur.mogrify(sql,[user["userId"]])
    cur.execute(sql,[user["userId"]])
    print cur.rowcount
    if cur.rowcount < 1:
        return False
    else:
        return True


@service.get()
def service_get(request):
    
    login = pyramid.security.authenticated_userid(request)
    did_fail = False
    user = None
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
        if user is not None:
            userObj = user.get_userObj()
            success = checkValidUser(userObj)
            if not success:     # ensure only reviewers & admins can login
                return conference_abstract.util.generate_template('loginPoster.mako',{"user":None,"request":request,"pageTitle":"Login"})

                #loc = request.route_url('logoutPoster')
                #return HTTPFound(location=loc)
                '''
                templateVars = {
                    "user": user,
                    "title": "No Access",
                    "message": "Sorry, access is now restricted to poster and lightning talk submission"
                }
                return conference_abstract.util.generate_template('abstractPosterMessage.mako',templateVars)'''
                
            else:
                loc = request.route_url('dashboardPoster')
                return HTTPFound(location=loc)

    return conference_abstract.util.generate_template('loginPoster.mako',{"user":user,"request":request,"pageTitle":"Login"})

@service.post()
def service_post(request):
    user = None
    did_fail = False
    templateVars = {       # for failed login attempt
        'message':'Your email or password is incorrect.<br/> Please try again',
        #'user': user,
        'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Login"}],
        'pageTitle':'Login',
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
        #print loginCheck
        #Hard coding allowed users
        #allowedUsers = ['rrajendra','anjalisilva','cwei','ema','sratnasi','johanssj','cbertrand','dchan','drea','melbastami','mmilton','stoneham','rmanjunath','sratnasingham1','c.wei1','asauk','boldhoc','telliott2','ezakharov','sprosser','tbraukmann']
        #if login not in allowedUsers:
        #    loginCheck = False

        if user and loginCheck != False:
            userObj = user.get_userObj()
            user.check_userLevel()
            success = checkValidUser(userObj)
            print success
            if not success:     # ensure only reviewers & admins can login
                templateVars = {
                    "user": user,
                    "title": "No Access",
                    "message": "Sorry, access is now restricted to poster and lightning talk submission"
                }
                return conference_abstract.util.generate_template('abstractPosterMessage.mako',templateVars)
            else:
                # Create session and set cookies
                headers = pyramid.security.remember(request, login+"|"+str(loginCheck))
                session = request.session
                session['fullname'] = userObj["fullname"]
                session['userId'] = userObj["userId"]
                return HTTPFound(location="/dashboardPoster", headers=headers)
        did_fail = True

    # Handling error response
    
    user = None
    templateVars['failed_attempt']=did_fail
    templateVars['login']=login

    #token = login.split("|")[1] if login is not None else ""
    return conference_abstract.util.generate_template('loginPoster.mako',templateVars)