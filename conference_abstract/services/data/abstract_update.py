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
from conference_abstract.services.data.abstract_info import getAbstractFullDetails
import time

info_desc = """\
This will get the abstract info
"""
service = Service(name='abstractUpdate', path='/abstract/{abstractId}/update',description=info_desc)

def getFullname(firstname,middle,lastname):
    if middle.strip() == "":
        return firstname + " " + lastname
    else:
        return firstname + " " + middle + " " + lastname

def getAbstract(abstractId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    abstracts = []
    currentCategory = 0
    try:
        sql = """select id, fk_submitter,review_status from abstracts where abstracts.id=%s """
        print cur.mogrify(sql,(abstractId,))
        cur.execute(sql,(abstractId,))
        for row in cur.fetchall():
            abstracts.append({"id":row["id"],"submitter":row["fk_submitter"],"review_status":row["review_status"]})
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return abstracts

def updateAbstract(abstractId, status):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    try:
        sql = """update abstracts set review_status = %s, modification_date = now() where abstracts.id=%s """
        print cur.mogrify(sql,(status, abstractId,))
        cur.execute(sql,(status, abstractId,))
        cur.execute("insert into stats_and_dates (registered_participants, abstracts_received, conference_date, abstracts_deadline,seats_available)  (select registered_participants, abstracts_received+1, conference_date, abstracts_deadline,seats_available from stats_and_dates order by id desc limit 1)")
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        success = False
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.commit()
    conn.close()
    return success

@service.get()
def data_get(request):
    data = {
        'success': False,
    }
    params = request.GET
    abstractId = request.matchdict['abstractId']
    abstracts = None# getAbstract(abstractId)
    if abstracts is not None and len(abstracts)>0:
        data["abstract"] = abstracts[0]
        data["success"] = True
    return conference_abstract.util.generate_response(data)

@service.post()
def data_post(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    if login is not None:
        username = login.split("|")[0]
        userId = login.split("|")[1]
        user = conference_abstract.auth.check_user(request)
    data = {
        'success': False,
    }
    abstractId = request.matchdict['abstractId']
    abstracts,authors = getAbstractFullDetails(abstractId)
    print abstracts[0]["submitter"],userId
    #debug = True
    #if debug == True:
    #    data = request.POST
    #    return conference_abstract.util.generate_response(conference_abstract.util.jsonify(data))

    if abstracts is not None and len(abstracts)>0:
        if abstracts[0]["submitter"] == int(userId):
            abstract = abstracts[0]
            try:
                if abstract["review_status"].upper() == "UNSUBMITTED":
                    data["success"] = updateAbstract(abstractId, "SUBMITTED")
                    abstractAuthors = authors[int(abstractId)]
                    mailTo = []
                    authorNames = []
                    for author in abstractAuthors:
                        mailTo.append(author["email"])
                        authorNames.append(getFullname(author["first_name"], author["middle_initial"], author["last_name"]))
                    mailFrom = "abstracts@ibol.org"
                    mailSubject = "Submission Confirmation - 2017 International Barcode of Life Conference"
                    mailBody = """Dear Authors,

This is an automated email to confirm your submission of the following abstract for inclusion in the 2017 International Barcode of Life Conference.  

Abstract Title: %s

Abstract: 
%s

Authors: %s

Preferred Presentation Type: %s

Submitted by: %s

You abstract will be reviewed by the April 30th, 2017; you will be contacted by the scientific committee or session chairs by that date with a decision.

The submitter can view the status of this abstract submission at any time by checking your dashboard after logging into:
http://abstracts.dnabarcodes2017.org

Thank you, from the Conference Operating Committee
http://dnabarcodes2017.org/
"""
                    conference_abstract.util.sendMail( mailFrom, mailTo,  mailSubject, mailBody % (abstract["title"],abstract["abstract_text"],", ".join(authorNames), abstract["abstract_type"],abstract["submitter_name"]))


                else:
                    print "nothing to do"
            except Exception as e:
                print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
                print e
                success = False
                print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        #else:
        #    print type(abstracts[0]["submitter"]), type(userId)
        #is this the reviewer that will approve the abstract?
    return conference_abstract.util.generate_response(data)
