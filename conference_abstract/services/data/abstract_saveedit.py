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
This will get the abstract score info for a given chair
"""
service = Service(name='abstractSaveEdit', path='/abstract/{abstractId}/saveEdit/{accessKey}',description=info_desc)

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

def getCopyEditors(abstractId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    copyEditorId = None
    try:
        sql = """select fk_copyeditor from editor_assignments where fk_abstracts=%s """
        print cur.mogrify(sql,(abstractId,))
        cur.execute(sql,(abstractId,))
        if cur.rowcount > 0:
            result = cur.fetchone()
            copyEditorId = result["fk_copyeditor"]
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return copyEditorId

def getScore(abstractId, copyEditorId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    score = None
    suggestedTopic = None
    try:
        sql = """ select score, suggested_topic from abstracts_score where fk_abstracts = %s and fk_reviewer = %s order by score_date desc limit 1;"""
        print cur.mogrify(sql,(abstractId,copyEditorId,))
        cur.execute(sql,(abstractId,copyEditorId,))
        if cur.rowcount == 1:
            result = cur.fetchone()
            score = result["score"]
            suggestedTopic = result["suggested_topic"]
        else:
            score = "0"
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        success = False
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return success,score,suggestedTopic

def getAllScores(abstractId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    score = None
    suggestedTopic = None
    try:
        sql = """ select score from abstracts_score where fk_abstracts = %s order by score_date asc;"""
        print cur.mogrify(sql,(abstractId,))
        cur.execute(sql,(abstractId,))
        scores = []
        if cur.rowcount > 0:
            for row in cur.fetchall():
                scores.append(str(row["score"]))
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        success = False
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return success,scores
    
def saveAbstractEdit(abstractId,copyEditorId,editedAbstractText):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    try:
        sql = """update abstracts set abstract_text_edited = %s where id = %s RETURNING id;"""
        print cur.mogrify(sql,[editedAbstractText,abstractId])
        cur.execute(sql,[editedAbstractText,abstractId])
        result = cur.fetchone()
        print result
        sqlAbstractUpdate = """ update abstracts set modification_date = now(), review_status = %s where abstracts.id = %s"""
        print cur.mogrify(sqlAbstractUpdate,('EDITED', abstractId,))
        cur.execute(sqlAbstractUpdate,('EDITED', abstractId,))
        result = cur.rowcount
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
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        success = False
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return success,editor

def checkAccessKey(accessKey,user):
    if user.is_editor():
        if user.chairAccessKey == accessKey:
            return True
    return False
    
@service.get()
def data_get(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    data = {
        'success': False,
    }
    if login is not None:
        username = login.split("|")[0]
        userId = login.split("|")[1]
        user = conference_abstract.auth.check_user(request)
        if user.is_editor():
            abstractId = request.matchdict['abstractId']
            accessKey = request.matchdict['accessKey']
            #check that the accessKey sent matches the current one logged in
            if checkAccessKey(accessKey,user):
                #check that they have access to this abstract
                success,editor = checkEditor(abstractId,user.editorId)
                print ""
                print ""
                print success, editor, user.editorId
                print ""
                print ""
                if success:
                    #grab the score
                    debug = False
                    if debug == True:
                        data = request.POST
                        return conference_abstract.util.generate_response(conference_abstract.util.jsonify(data))
                    editedAbstractText = request.GET.get('editedText', None)
                    print ""
                    print ""
                    print data
                    print ""
                    print ""
                    if editedAbstractText is not None:
                        print editedAbstractText
                        success = saveAbstractEdit(abstractId, user.editorId, editedAbstractText)
                        data["success"] = success
    return conference_abstract.util.generate_response(data)

@service.post()
def data_post(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    data = {
        'success': False,
    }
    if login is not None:
        username = login.split("|")[0]
        userId = login.split("|")[1]
        user = conference_abstract.auth.check_user(request)
        if user.is_editor():
            abstractId = request.matchdict['abstractId']
            accessKey = request.matchdict['accessKey']
            #check that the accessKey sent matches the current one logged in
            if checkAccessKey(accessKey,user):
                #check that they have access to this abstract
                success,editor = checkEditor(abstractId,user.editorId)
                print ""
                print ""
                print success, editor
                print ""
                print ""
                if success:
                    #grab the score
                    debug = False
                    if debug == True:
                        data = request.POST
                        return conference_abstract.util.generate_response(conference_abstract.util.jsonify(data))
                    editedAbstractText = request.POST.get('editedText', None)
                    print ""
                    print ""
                    print data
                    print ""
                    print ""
                    if editedAbstractText is not None:
                        success = saveAbstractEdit(abstractId, user.editorId, editedAbstractText)
                        data["success"] = success
    return conference_abstract.util.generate_response(data)
