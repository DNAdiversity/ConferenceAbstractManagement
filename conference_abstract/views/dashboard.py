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
from conference_abstract.views.login import getValidLogins
import unicodedata

info_desc = """\
This is the dashboard page for the dna conference
"""

service = Service(name='dashboard', path='/dashboard', description=info_desc)

def getAbstracts(user):
    if user.is_admin():
        submitter = "admin"
    elif user.userId == 45:
        submitter = "reviewer"
    elif user.chairId is not None:
        submitter = "reviewer"
    elif user.editorId is not None:
        submitter = "editor"
    else:
        submitter = user.userId
    print "========================================"
    print "="
    print "="
    print "submitter is :",submitter
    print "="
    print "="
    print "========================================"
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    abstracts = []
    authors = {}
    currentCategory = 0
    try:
        if submitter == "admin":
            sql = """select abstracts.id, abstract_type, abstracts.title, submission_date, modification_date, selected_topics, review_status, cusers.salutation || ' ' || cusers.first_name || ' ' || cusers.middle_initial || ' ' || cusers.last_name as submitter_name, fk_submitter from abstracts left join cusers on abstracts.fk_submitter = cusers.id where review_status != 'UNSUBMITTED' order by abstracts.id"""
            print cur.mogrify(sql)
            cur.execute(sql)
            for row in cur.fetchall():
                abstracts.append({"id":row["id"],"abstract_type":row["abstract_type"],"title":row["title"],"submission_date":row["submission_date"],"modification_date":row["modification_date"],"review_status":row["review_status"],"submitter_name":row["submitter_name"],"categories":row["selected_topics"],"submitter":row["fk_submitter"]})
            sqlAuthor = """select fk_abstract, fname || ' ' || mname || ' ' || lname as fullname from authorship order by id"""
            print cur.execute(sqlAuthor)
            cur.execute(sqlAuthor)
            print "Getting all the Authors!!!"
        elif submitter == "reviewer":
            sql = """select abstracts.id, abstract_type, abstracts.title, submission_date, modification_date, selected_topics, review_status, cusers.salutation || ' ' || cusers.first_name || ' ' || cusers.middle_initial || ' ' || cusers.last_name as submitter_name, fk_submitter from review_assignments left join abstracts on review_assignments.fk_abstracts = abstracts.id left join cusers on abstracts.fk_submitter = cusers.id where fk_reviewer = %s order by abstracts.id"""
            print cur.mogrify(sql,(user.chairId,))
            cur.execute(sql,(user.chairId,))
            for row in cur.fetchall():
                abstracts.append({"id":row["id"],"abstract_type":row["abstract_type"],"title":unicodedata.normalize('NFKD', row["title"].decode('unicode-escape')).encode('ascii', 'ignore'),"submission_date":row["submission_date"],"modification_date":row["modification_date"],"review_status":row["review_status"],"submitter_name":unicodedata.normalize('NFKD', row["submitter_name"].decode('unicode-escape')).encode('ascii', 'ignore'),"categories":row["selected_topics"],"submitter":row["fk_submitter"]})
            sqlAuthor = """select fk_abstract, fname || ' ' || mname || ' ' || lname as fullname from authorship where fk_abstract in (select fk_abstracts from review_assignments where fk_reviewer = %s) order by id"""
            print cur.mogrify(sqlAuthor,(user.chairId,))
            cur.execute(sqlAuthor,(user.chairId,))
        elif submitter == "editor":
            sql = """select abstracts.id, abstract_type, abstracts.title, submission_date, modification_date, selected_topics, review_status, cusers.salutation || ' ' || cusers.first_name || ' ' || cusers.middle_initial || ' ' || cusers.last_name as submitter_name, fk_submitter from editor_assignments left join abstracts on editor_assignments.fk_abstracts = abstracts.id left join cusers on abstracts.fk_submitter = cusers.id where fk_copyeditor = %s order by abstracts"""
            print cur.mogrify(sql,(user.editorId,))
            cur.execute(sql,(user.editorId,))
            for row in cur.fetchall():
                abstracts.append({"id":row["id"],"abstract_type":row["abstract_type"],"title":unicodedata.normalize('NFKD', row["title"].decode('unicode-escape')).encode('ascii', 'ignore'),"submission_date":row["submission_date"],"modification_date":row["modification_date"],"review_status":row["review_status"],"submitter_name":unicodedata.normalize('NFKD', row["submitter_name"].decode('unicode-escape')).encode('ascii', 'ignore'),"categories":row["selected_topics"],"submitter":row["fk_submitter"]})
            sqlAuthor = """select fk_abstract, fname || ' ' || mname || ' ' || lname as fullname from authorship where fk_abstract in (select fk_abstracts from editor_assignments where fk_copyeditor = %s) order by id"""
            print cur.mogrify(sqlAuthor,(user.editorId,))
            cur.execute(sqlAuthor,(user.editorId,))
            print "finished query"
        else:
            sql = """select id, abstract_type, title, submission_date, modification_date, selected_topics, review_status, fk_submitter from abstracts where fk_submitter=%s order by abstracts.id"""
            print cur.mogrify(sql,( 
                submitter,
            ))
            cur.execute(sql,( 
                submitter,
            ))
            for row in cur.fetchall():
                abstracts.append({"id":row["id"],"abstract_type":row["abstract_type"],"title":unicodedata.normalize('NFKD', row["title"].decode('unicode-escape')).encode('ascii', 'ignore'),"submission_date":row["submission_date"],"modification_date":row["modification_date"],"review_status":row["review_status"],"categories":row["selected_topics"],"submitter":row["fk_submitter"]})
            sqlAuthor = """select fk_abstract, fname || ' ' || mname || ' ' || lname as fullname from authorship where fk_abstract in (select id from abstracts where fk_submitter = %s) order by id"""
            print cur.mogrify(sqlAuthor,(submitter,))
            cur.execute(sqlAuthor,(submitter,))
        for row in cur.fetchall():
            abstractId = row["fk_abstract"]
            if abstractId not in authors:
                authors[abstractId] = []
            #authors[abstractId].append(unicodedata.normalize('NFKD,', row["fullname"].decode('unicode-escape')).encode('ascii', 'ignore'))
            authors[abstractId].append(row["fullname"])
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    print "========== \/ look here \/ ========="
    print authors
    print "========== /\ look here /\ ========="
    return abstracts,authors

def getChairs():
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    chairs = []
    sql = "select id, topics, categories, fullname from chairs;"
    try:
        print cur.mogrify(sql)
        cur.execute(sql)
        for row in cur.fetchall():
            chairs.append({row["id"],row["topics"],row["categories"],row["fullname"]})
        
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return chairs
    
@service.get()
def service_get(request):
    lockedDown = True
    login = pyramid.security.authenticated_userid(request)
    user = None
    userId = 0
    if login is not None:
        user = conference_abstract.auth.check_user(request)
    if user == False or user == None:
        headers = pyramid.security.forget(request)
        loc = request.route_url('login')
        return HTTPFound(location=loc)
    else:
        if lockedDown == True:
            userObj = user.get_userObj()
            user.check_userLevel()
            if user.get_userLevel() is None and userObj["userId"] not in getValidLogins():     # ensure only reviewers & admins can login
                templateVars = {
                    "user": user,
                    "title": "No Access",
                    "message": "Sorry, access is now restricted to reviewers and conference coordinators"
                }
                return conference_abstract.util.generate_template('abstractThankYouMessage.mako',templateVars)

    ##TODO this is only when locked down
    abstracts,authors = getAbstracts(user)
    print userId, abstracts, authors, login
    templateVars = {
        "user":user,
        "message":"",
        "abstracts":abstracts,
        "authors":authors,
        "chairs":getChairs()
    }
    return conference_abstract.util.generate_template('dashboard.mako',templateVars)

