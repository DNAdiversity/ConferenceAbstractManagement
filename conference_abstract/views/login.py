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

service = Service(name='login', path='/login', description=info_desc)

#NOTE: This is used on other pages so this will centralize the check
def getValidLogins():
    return [83,197, 450, 218, 637,468,650,651,522, 473]

@service.get()
def service_get(request):
    login = pyramid.security.authenticated_userid(request)
    did_fail = False
    user = None
    templateVars = {"user":user,"request":request,"pageTitle":"Login"}
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
        if user is not None:
            userObj = user.get_userObj()
            user.check_userLevel()
            templateVars["user"] = user
            if user.get_userLevel() is None and userObj["userId"] not in getValidLogins():     # ensure only reviewers & admins can login
                templateVars['message']="Sorry, you do not have access"
            else:
                loc = request.route_url('dashboard')
                return HTTPFound(location=loc)

    return conference_abstract.util.generate_template('login.mako',templateVars)

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

            if user.get_userLevel() is None and userObj["userId"] not in getValidLogins():     # ensure only reviewers & admins can login
                templateVars = {
                    "user": user,
                    "title": "No Access",
                    "message": "Sorry, access is now restricted to reviewers and conference coordinators",
                    "showButton": "loginPoster"
                }
                return conference_abstract.util.generate_template('abstractThankYouMessage.mako',templateVars)
            else:

                # Create session and set cookies
                headers = pyramid.security.remember(request, login+"|"+str(loginCheck))
                session = request.session
                session['fullname'] = userObj["fullname"]
                session['userId'] = userObj["userId"]
                return HTTPFound(location="/dashboard", headers=headers)
        did_fail = True

    # Handling error response

    user = None
    templateVars['failed_attempt']=did_fail
    templateVars['login']=login

    #token = login.split("|")[1] if login is not None else ""
    return conference_abstract.util.generate_template('login.mako',templateVars)