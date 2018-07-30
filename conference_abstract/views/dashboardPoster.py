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
from conference_abstract.views.login_abstract import checkValidUser
import unicodedata

info_desc = """\
This is the dashboard page for the dna conference
"""

service = Service(name='dashboardPoster', path='/dashboardPoster', description=info_desc)

def getAbstracts(user):
    abstracts = []
    authors = {}
    if user.is_admin():
        submitter = "admin"
    elif user.userId == 45:
        #submitter = "reviewer"
        return abstracts, authors
    elif user.chairId is not None:
        #submitter = "reviewer"
        return abstracts, authors
    elif user.editorId is not None:
        #submitter = "editor"
        return abstracts, authors
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
    currentCategory = 0
    try:
        if submitter == "admin":
            sql = """select * from (
select * from 
(select abstracts.id, abstracts.title, abstract_type, abstract_text, abstract_text_edited, abstracts.abstract_attachment, authorlist.all_authors, abstracts.fk_submitter, abstracts.abstract_attachment
from abstracts 
left join authorlist on authorlist.fk_abstract = abstracts.id
where abstract_type in ('Poster') and review_status = 'EDITED') as test
union
(select abstracts.id, abstracts.title, abstract_type, abstract_text, abstract_text_edited, abstracts.abstract_attachment, authorlist.all_authors, abstracts.fk_submitter, abstracts.abstract_attachment from agenda 
left join abstracts on agenda.fk_abstracts = abstracts.id
left join authorlist on authorlist.fk_abstract = abstracts.id
where abstracts.abstract_type = 'Lightning Talk'
) ) as available_abstracts order by available_abstracts.id;"""
            print cur.mogrify(sql)
            cur.execute(sql)
            for row in cur.fetchall():
                #code = int(row["id"])/3.1415*1234567890
                abstracts.append({"id":row["id"],"abstract_type":row["abstract_type"],"title":row["title"],"submitter":row["fk_submitter"],"attachment":row["abstract_attachment"]})
            sqlAuthor = """select fk_abstract, fname || ' ' || mname || ' ' || lname as fullname from authorship order by id"""
            print cur.execute(sqlAuthor)
            cur.execute(sqlAuthor)
            print "Getting all the Authors!!!"
        else:
            sql = """select * from (
select * from 
(select abstracts.id, abstracts.title, abstract_type, abstract_text, abstract_text_edited, abstracts.abstract_attachment, authorlist.all_authors, abstracts.fk_submitter, abstracts.abstract_attachment
from abstracts 
left join authorlist on authorlist.fk_abstract = abstracts.id
where abstract_type in ('Poster') and review_status = 'EDITED') as test
union
(select abstracts.id, abstracts.title, abstract_type, abstract_text, abstract_text_edited, abstracts.abstract_attachment, authorlist.all_authors, abstracts.fk_submitter, abstracts.abstract_attachment from agenda 
left join abstracts on agenda.fk_abstracts = abstracts.id
left join authorlist on authorlist.fk_abstract = abstracts.id
where abstracts.abstract_type = 'Lightning Talk'
) ) as available_abstracts where fk_submitter=%s order by available_abstracts.id"""
            print cur.mogrify(sql,( 
                submitter,
            ))
            cur.execute(sql,( 
                submitter,
            ))
            for row in cur.fetchall():
                abstracts.append({"id":row["id"],"abstract_type":row["abstract_type"],"title":row["title"],"submitter":row["fk_submitter"],"attachment":row["abstract_attachment"]})
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
            success = checkValidUser(userObj)
            print success
            if not success:     # ensure only poster & admins can login
                templateVars = {
                    "user": user,
                    "title": "No Access",
                    "message": "Sorry, access is now restricted to poster and lightning talk submission"
                }
                return conference_abstract.util.generate_template('abstractPosterMessage.mako',templateVars)

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
    return conference_abstract.util.generate_template('dashboardPoster.mako',templateVars)

