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
import unicodedata

info_desc = """\
This is the contact page
"""

service = Service(name='contactus', path='/contactus', description=info_desc)


@service.get()
def service_get(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
    return conference_abstract.util.generate_template('contactUs.mako',{"user":user,"request":request})

@service.post()
def service_post(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
    contactName = request.POST.get('contactname', None)
    contactLastname = request.POST.get('contactlastname', None)
    contactEmail = request.POST.get('contactemail', None)
    contactSubject = request.POST.get('contactsubject', None)
    contactMessage = request.POST.get('contactmessage', None)
    fromAddress = contactEmail
    fromName = ""
    sep = ""
    if contactName is not None:
        fromName += contactName
        sep = " "
    if contactLastname is not None:
        fromName += sep + contactLastname
    if fromName.strip() != "":
        contactMessage = fromName+"\n"+fromAddress+"\n\n"+contactMessage
        fromAddress = fromName + ' <' + fromAddress + '>'
    try:
        contactSelfEmail = request.POST.get('contactselfemail', None)
    except:
        contactSelfEmail = False
    toAddress = ["abstracts@ibol.org"]
    if contactSelfEmail == "True":
        if fromAddress != "":
            toAddress.append(fromAddress)
    if contactSubject is None:
        contactSubject = "Contact Us Message"
    else:
        contactSubject = unicodedata.normalize('NFKD', contactSubject).encode('ascii', 'ignore')
    contactMessage = unicodedata.normalize('NFKD', contactMessage).encode('ascii', 'ignore')
    conference_abstract.util.sendMail(fromAddress,toAddress,contactSubject,contactMessage)
    return conference_abstract.util.generate_template('contactUsSuccess.mako',{"user":user,"request":request})

