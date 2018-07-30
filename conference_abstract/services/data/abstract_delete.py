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
This will get the abstract info
"""
service = Service(name='abstractDelete', path='/abstract/{abstractId}/delete',description=info_desc)

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

def deleteAbstract(abstractId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    try:
        sqlAuthors = """delete from authorship where fk_abstract = %s"""
        print cur.mogrify(sqlAuthors,(abstractId,))
        cur.execute(sqlAuthors,(abstractId,))
        sql = """delete from abstracts where abstracts.id=%s """
        print cur.mogrify(sql,(abstractId,))
        cur.execute(sql,(abstractId,))
        #cur.execute("insert into stats_and_dates (registered_participants, abstracts_received, conference_date, abstracts_deadline,seats_available)  (select registered_participants, abstracts_received-1, conference_date, abstracts_deadline,seats_available from stats_and_dates order by id desc limit 1)")
            
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
    abstracts = getAbstract(abstractId)
    print ""
    print abstracts[0]["submitter"],userId
    debug = False
    if debug == True:
        data = request.POST
        return conference_abstract.util.generate_response(conference_abstract.util.jsonify(data))

    if abstracts is not None and len(abstracts)>0:
        if abstracts[0]["submitter"] == int(userId):
            if abstracts[0]["review_status"].lower() == "unsubmitted":
                print "I should delete"
                data["success"] = deleteAbstract(abstractId)
            else:
                print "nothing to do"
        #else:
        #    print type(abstracts[0]["submitter"]), type(userId)
        #is this the reviewer that will approve the abstract?
    return conference_abstract.util.generate_response(data)
