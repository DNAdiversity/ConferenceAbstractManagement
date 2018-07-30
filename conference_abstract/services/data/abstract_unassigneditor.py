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
This will get the unassign an editor
"""
service = Service(name='abstractEditorUnassign', path='/abstract/{abstractId}/unassignEditor',description=info_desc)

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

def unassignAbstractEditor(abstractId,copyEditorId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    try:
        sql = """delete from editor_assignments where fk_abstracts = %s and fk_copyeditor = %s;"""
        print cur.mogrify(sql,(abstractId,copyEditorId,))
        cur.execute(sql,(abstractId,copyEditorId,))
        #result = cur.fetchone()
        #print result
        #TODO do we update the status when there are no assigned?
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        success = False
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.commit()
    conn.close()
    return success

def checkEditor(abstractId, copyEditorId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    editor = {}
    try:
        sql = """select * from copyeditors where id = %s"""
        print cur.mogrify(sql,(copyEditorId,))
        cur.execute(sql,(copyEditorId,))
        rowcount = cur.rowcount
        print rowcount
        if rowcount == 0 or rowcount > 1:
            success = False
        else:
            result = cur.fetchone()
            editor["fullname"] = result["fullname"]
            editor["email"] = result["email"]
            editor["accesskey"] = result["accesskey"]
            sql = """select * from editor_assignments where fk_abstracts = %s and fk_copyeditor = %s;"""
            print cur.mogrify(sql,(abstractId, copyEditorId,))
            cur.execute(sql,(abstractId, copyEditorId,))
            result = cur.rowcount
            print result
            if result != 1:
                success = False
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR <<<<<<<<<<<<<<"
        print e
        success = False
        print ">>>>>>>>>> ERROR ERROR ERROR <<<<<<<<<<<<<<"
    conn.close()
    return success,editor

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
    copyEditorId = request.POST.get('copyEditorId', 0)
    abstracts = getAbstract(abstractId)

    print ""
    debug = False
    if debug == True:
        data = request.POST
        if abstracts is not None and len(abstracts)>0:
            success, editor = checkEditor(abstractId, copyEditorId)
            data["canIUnAssign"] = success
            data["editor"] = editor
            data["doesAbstractExist"] = len(abstracts)
        else:
            data["success"] = False;
        return conference_abstract.util.generate_response(conference_abstract.util.jsonify(data))

        #abstract exists so check that it isn't 0 for the editor
        
    if abstracts is not None and len(abstracts)>0:
        print "Found the abstract"
        success, editor = checkEditor(abstractId, copyEditorId)
        if success:
            print "I should unassign"
            success = unassignAbstractEditor(abstractId,copyEditorId)
            data["success"] = success
            if success == True:
                #send and email
                
                print data
            else:
                print "nothing to do"
        else:
            print success,"not successful"
        #    print type(abstracts[0]["submitter"]), type(userId)
        #is this the editor that will approve the abstract?
    return conference_abstract.util.generate_response(data)
