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
import string
import random
import unicodedata


info_desc = """\
This is the registration page for the dna conference
"""

service = Service(name='registration', path='/registration', description=info_desc)

def generateNewPassword():
    chars = string.letters + string.digits
    passwordSize = 8
    return ''.join((random.choice(chars)) for x in range(passwordSize))

@service.get()
def service_get(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    if login is not None:
        user = conference_abstract.auth.check_user(request)
    templateVars = {
        "user":user,
        "request":request,
        "pageTitle":"",
        "pageDesc":""
    }
    return conference_abstract.util.generate_template('registration.mako',templateVars)

@service.post()
def service_post(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    if login is not None:
        user = conference_abstract.auth.check_user(request)
    registrationSuccess = False
    firstname = request.POST.get('firstname', None)
    middleinitial = request.POST.get('middleinitial', None)
    lastname = request.POST.get('lastname', '')
    institution = request.POST.get('institution', None)
    department = request.POST.get('department', None)
    email = request.POST.get('email', None)
    country = request.POST.get('country', None)
    salutation = request.POST.get('salutation', None)
    address1 = request.POST.get('address1', None)
    address2 = request.POST.get('address2', None)
    city = request.POST.get('city', None)
    province_state = request.POST.get('province_state', None)
    postalcode = request.POST.get('postalcode', None)
    templateVars = {
        'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Registration"}],
        'pageTitle':'Registration Failed',
        'pageDesc':'',
        'success': False
    }
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor()
    sql = """select * from cusers where email ilike %s;"""
    cur.execute(sql,[email.strip()])
    duplicate = False
    if cur.rowcount > 0:
        duplicate = True
    print email, firstname, lastname, institution, country
    if email != "" and firstname != "" and lastname != "" and institution != "" and country != "" and duplicate == False:
        registrationSuccess = True
        newPassword = generateNewPassword()
        sql = """insert into cusers (first_name, middle_initial, last_name, institution, department, email, country, password, salutation, address1, address2, city, province_state, postalcode) 
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"""
        print cur.mogrify( sql, 
            (firstname, 
            middleinitial, 
            lastname, 
            institution, 
            department,
            email, 
            country, 
            newPassword,
            salutation,
            address1,
            address2,
            city,
            province_state,
            postalcode) )
        try:
            cur.execute( sql, 
                (firstname, 
                middleinitial, 
                lastname, 
                institution, 
                department,
                email, 
                country, 
                newPassword,
                salutation,
                address1,
                address2,
                city,
                province_state,
                postalcode) )
            userId = cur.fetchone()[0]
            conn.commit();
        except Exception as e:
            print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
            print e
            print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        #print "sleeping ....zzzzZZZZ"
        #time.sleep(5)
        #print "done sleep"
        if userId is not None:
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
            firstname = unicodedata.normalize('NFKD', firstname).encode('ascii', 'ignore')
            lastname = unicodedata.normalize('NFKD', lastname).encode('ascii', 'ignore')
            institution = unicodedata.normalize('NFKD', institution).encode('ascii', 'ignore')
            email = unicodedata.normalize('NFKD', email).encode('ascii', 'ignore')
            conference_abstract.util.sendMail("abstracts@ibol.org",[email],"Conference Abstract Account",message % (firstname + ' ' + lastname, email, newPassword))
            #print userId[0]
            templateVars = {
                'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Registration"}],
                'pageTitle':'Registration Success',
                'pageDesc':'',
                'email':email, 
                'password':newPassword,
                'success': True
            }
        else:
            templateVars = {
            'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Registration"}],
                'pageTitle':'Registration Failed',
                'pageDesc':'',
                'success': False
            }
        return conference_abstract.util.generate_template('registrationSuccess.mako',templateVars)
        #return conference_abstract.util.generate_template('registrationSuccess.mako',templateVars)
    else:
        templateVars = {
            'message':'',
            'user': user,
            'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Registration"}],
            'pageTitle':'',
            "request":request
        }
        templateVars["formData"] = request.POST
        return conference_abstract.util.generate_template('registration.mako',templateVars)

