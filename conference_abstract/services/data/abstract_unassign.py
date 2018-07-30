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
This will get the unassign a reviewer
"""
service = Service(name='abstractUnassign', path='/abstract/{abstractId}/unassign',description=info_desc)

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

def unassignAbstract(abstractId,reviewerId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    try:
        sql = """delete from review_assignments where fk_abstracts = %s and fk_reviewer = %s;"""
        print cur.mogrify(sql,(abstractId,reviewerId,))
        cur.execute(sql,(abstractId,reviewerId,))
        #result = cur.fetchone()
        #print result
        #TODO do we update the status when there are no assigned?
        '''
        sqlAbstractUpdate = """ update abstracts set modification_date = now(), review_status = %s where abstracts.id = %s"""
        print cur.mogrify(sqlAbstractUpdate,('ASSIGNED', abstractId,))
        cur.execute(sqlAbstractUpdate,('ASSIGNED', abstractId,))
        result = cur.rowcount
        '''
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        success = False
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.commit()
    conn.close()
    return success

def checkReviewer(abstractId, reviewerId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    reviewer = {}
    try:
        sql = """select * from chairs where id = %s"""
        print cur.mogrify(sql,(reviewerId,))
        cur.execute(sql,(reviewerId,))
        rowcount = cur.rowcount
        print rowcount
        if rowcount == 0 or rowcount > 1:
            success = False
        else:
            result = cur.fetchone()
            reviewer["fullname"] = result["fullname"]
            reviewer["email"] = result["email"]
            reviewer["accesskey"] = result["accesskey"]
            sql = """select * from review_assignments where fk_abstracts = %s and fk_reviewer = %s;"""
            print cur.mogrify(sql,(abstractId, reviewerId,))
            cur.execute(sql,(abstractId, reviewerId,))
            result = cur.rowcount
            print result
            if result != 1:
                success = False
            #TODO Do we see if they have scored the abstract?
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        success = False
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return success,reviewer

@service.get()
def data_get(request):
    data = {
        'success': False,
    }
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
    reviewerId = request.POST.get('reviewerId', 0)
    abstracts = getAbstract(abstractId)

    print ""
    debug = False
    if debug == True:
        data = request.POST
        if abstracts is not None and len(abstracts)>0:
            success, reviewer = checkReviewer(abstractId, reviewerId)
            data["canIUnAssign"] = success
            data["reviewer"] = reviewer
            data["doesAbstractExist"] = len(abstracts)
        else:
            data["success"] = False;
        return conference_abstract.util.generate_response(conference_abstract.util.jsonify(data))

        #abstract exists so check that it isn't 0 for the reviewer
        
    if abstracts is not None and len(abstracts)>0:
        print "Found the abstract"
        success, reviewer = checkReviewer(abstractId, reviewerId)
        if success:
            print "I should unassign"
            success = unassignAbstract(abstractId,reviewerId)
            data["success"] = success
            if success == True:
                #send and email
                
                print data
            else:
                print "nothing to do"
        #else:
        #    print type(abstracts[0]["submitter"]), type(userId)
        #is this the reviewer that will approve the abstract?
    return conference_abstract.util.generate_response(data)
