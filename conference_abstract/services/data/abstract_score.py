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
service = Service(name='abstractScore', path='/abstract/{abstractId}/score/{accessKey}',description=info_desc)

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

def getReviewer(abstractId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    reviewerId = None
    try:
        sql = """select fk_reviewer from review_assignments where fk_abstracts=%s """
        print cur.mogrify(sql,(abstractId,))
        cur.execute(sql,(abstractId,))
        if cur.rowcount > 0:
            result = cur.fetchone()
            reviewerId = result["fk_reviewer"]
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return reviewerId

def getScore(abstractId, reviewerId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    score = None
    suggestedTopic = None
    try:
        sql = """ select score, suggested_topic from abstracts_score where fk_abstracts = %s and fk_reviewer = %s order by score_date desc limit 1;"""
        print cur.mogrify(sql,(abstractId,reviewerId,))
        cur.execute(sql,(abstractId,reviewerId,))
        if cur.rowcount == 1:
            result = cur.fetchone()
            score = result["score"]
            suggestedTopic = result["suggested_topic"]
        else:
            score = ""
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
    scores = None
    editor_scores = None
    suggestedTopic = None
    try:
        sql = """ select editor_score, score from abstracts_score where fk_abstracts = %s order by score_date asc;"""
        print cur.mogrify(sql,(abstractId,))
        cur.execute(sql,(abstractId,))
        scores = []
        editor_scores = []
        if cur.rowcount > 0:
            for row in cur.fetchall():
                scores.append(str(row["score"]))
                editor_scores.append(str(row["editor_score"]))
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        success = False
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return success,scores,editor_scores
    
def assignScore(abstractId,reviewerId,score,suggestedTopic,notes):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    try:
        sql = """insert into abstracts_score (fk_abstracts, fk_reviewer, score, suggested_topic, score_date, notes) values (%s, %s, %s, %s, now(), %s) RETURNING id;"""
        print cur.mogrify(sql,[abstractId,reviewerId,score,suggestedTopic,notes])
        cur.execute(sql,[abstractId,reviewerId,score,suggestedTopic,notes])
        result = cur.fetchone()
        print result
        sqlAbstractUpdate = """ update abstracts set modification_date = now(), review_status = %s where abstracts.id = %s"""
        print cur.mogrify(sqlAbstractUpdate,('REVIEWED', abstractId,))
        cur.execute(sqlAbstractUpdate,('REVIEWED', abstractId,))
        result = cur.rowcount
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
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        success = False
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return success,reviewer

def checkAccessKey(accessKey,user):
    if user.is_reviewer():
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
        if user.is_reviewer():
            abstractId = request.matchdict['abstractId']
            accessKey = request.matchdict['accessKey']
            #check that the accessKey sent matches the current one logged in
            if checkAccessKey(accessKey,user):
                #check that they have access to this abstract
                success,reviewer = checkReviewer(abstractId,user.chairId)
                if success:
                    #grab the score
                    success,score,suggestedTopic = getScore(abstractId, user.chairId)
                    data["success"] = success
                    if success:
                        data["score"] = score
                        data["suggestedTopic"] = suggestedTopic
                        success, scores, editor_scores = getAllScores(abstractId)
                        if success:
                            data["scores"] = ",".join(scores)
                            data["editorScores"] = ",".join(editor_scores)
        elif user.is_admin():
            # we are the admin so we see all
            abstractId = request.matchdict['abstractId']
            reviewerId = getReviewer(abstractId)
            success,score,suggestedTopic = getScore(abstractId, reviewerId)
            data["success"] = success
            if success:
                data["score"] = score
                data["suggestedTopic"] = suggestedTopic
                success, scores, editor_scores = getAllScores(abstractId)
                if success:
                    data["scores"] = ",".join(scores)
                    data["editorScores"] = ",".join(editor_scores)

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
        if user.is_reviewer():
            abstractId = request.matchdict['abstractId']
            accessKey = request.matchdict['accessKey']
            #check that the accessKey sent matches the current one logged in
            if checkAccessKey(accessKey,user):
                #check that they have access to this abstract
                success,reviewer = checkReviewer(abstractId,user.chairId)
                print ""
                print ""
                print success, reviewer
                print ""
                print ""
                if success:
                    #grab the score
                    debug = False
                    if debug == True:
                        data = request.POST
                        return conference_abstract.util.generate_response(conference_abstract.util.jsonify(data))
                    score = request.POST.get('score', None)
                    suggestedTopic = request.POST.get('suggestedTopic',None)
                    notes = request.POST.get('notes',None)
                    if suggestedTopic == "":
                        suggestedTopic = None
                    print ""
                    print ""
                    print data
                    print ""
                    print ""
                    if score is not None:
                        success = assignScore(abstractId, user.chairId, score, suggestedTopic, notes)
                        data["success"] = success
    return conference_abstract.util.generate_response(data)
