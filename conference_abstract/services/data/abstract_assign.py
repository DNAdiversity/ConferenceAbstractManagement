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
import unicodedata


info_desc = """\
This will get the abstract info
"""
service = Service(name='abstractAssign', path='/abstract/{abstractId}/assign',description=info_desc)

def getAbstract(abstractId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    abstracts = []
    currentCategory = 0
    try:
        sql = """select title, abstract_type, abstract_text,
string_agg(replace(authorship.fname || ' ' || authorship.mname || ' ' || authorship.lname, '  ',' '), ', ') as authors
from abstracts 
left join authorship on abstracts.id = authorship.fk_abstract
where abstracts.id = %s
group by fk_abstract, title, abstract_type, abstract_text
"""
        print cur.mogrify(sql,(abstractId,))
        cur.execute(sql,(abstractId,))
        for row in cur.fetchall():
            abstracts.append({"title":row["title"],"text":row["abstract_text"],"authors":row["authors"]})
    except Exception as e:
        print "<<<<<<<<<<<<<< ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print "<<<<<<<<<<<<<< ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return abstracts

def assignAbstract(abstractId,reviewerId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    try:
        sql = """insert into review_assignments (fk_abstracts, fk_reviewer, assigned_date) values (%s, %s, now()) RETURNING id;"""
        print cur.mogrify(sql,(abstractId,reviewerId,))
        cur.execute(sql,(abstractId,reviewerId,))
        result = cur.fetchone()
        print result
        sqlAbstractUpdate = """ update abstracts set modification_date = now(), review_status = %s where abstracts.id = %s"""
        print cur.mogrify(sqlAbstractUpdate,('ASSIGNED', abstractId,))
        cur.execute(sqlAbstractUpdate,('ASSIGNED', abstractId,))
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
            if result > 0:
                success = False
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR <<<<<<<<<<<<<<"
        print e
        success = False
        print ">>>>>>>>>> ERROR ERROR ERROR <<<<<<<<<<<<<<"
    conn.close()
    return success,reviewer

def getChairInfo(reviewerId):
    #sql = """ select topics, categories from chairs where id = %s; """
    sql = """ select * from (select regexp_split_to_table(topics,'; ') as topic from chairs where id = %s) as chairtopics
left join topics on chairtopics.topic = topics.label 
    """
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    topics = ""
    categories = ""
    try:
        print cur.mogrify(sql,(reviewerId,))
        cur.execute(sql,(reviewerId,))
        rowcount = cur.rowcount
        print rowcount
        if rowcount == 0:
            success = False
        else:
            results = cur.fetchall()
            sep = ""
            for row in results:
                if row["category"] is not None and row["category"] != "":
                    print row["label"],row["category"]
                    topics += sep+row["label"]+" ("+row["category"]+")"
                    sep = ", "
        #if rowcount == 0 or rowcount > 1:
        #    success = False
        #else:
        #    result = cur.fetchone()
        #    print result
        #    topics = result["topics"]
        #    categories = result["categories"]
    except Exception as e:
        print "<<<<<<<<<<<<<< ERROR ERROR ERROR <<<<<<<<<<<<<<"
        print e
        success = False
        print "<<<<<<<<<<<<<< ERROR ERROR ERROR <<<<<<<<<<<<<<"
    conn.close()
    return success, topics, categories
    

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
            data["canIAssign"] = success
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
            print "I should assign"
            success = assignAbstract(abstractId,reviewerId)
            #success = True
            if success == True:
                #send and email
                abstract = getAbstract(abstractId)
                print "I assigned to ",reviewer["fullname"]
                success, topics, categories = getChairInfo(reviewerId)
                mailTo = [reviewer["email"]]
                mailFrom = "abstracts@ibol.org"
                mailSubject = "iBOL 2017 abstract review assignment notice - Automated Email"
                mailBody = """Dear Dr. %s,

Thank you for consenting to review abstracts for the 7th International Barcode of Life Conference.  We are writing to invite you to review an abstract that has been submitted under the topic(s) of %s.  The organizing committee values your expertise and would greatly appreciate your time in reviewing the submission. Please click the link below to access the reviewer dashboard on the conference abstract management system.  Once there, you will be able to score the abstract and provide brief comments.  If you are unable to review the abstract, please respond to this email indicating so.

Submission to Review:
Title: %s
Authors: %s
Abstract: 

%s


To perform the review or pass it to another reviewer, click on the following link:
http://abstracts.dnabarcodes2017.org/loginReviewer/%s

If you would prefer to be removed from our reviewer list, please email abstracts@ibol.org

Thank you,
Conference Operating Committee
http://dnabarcodes2017.org/

"""

                conference_abstract.util.sendMail(mailFrom,mailTo,mailSubject,mailBody % (reviewer["fullname"],topics,unicodedata.normalize('NFKD', abstract[0]["title"].decode('unicode-escape')).encode('ascii', 'ignore'),unicodedata.normalize('NFKD', abstract[0]["authors"].decode('unicode-escape')).encode('ascii', 'ignore'),unicodedata.normalize('NFKD', abstract[0]["text"].decode('unicode-escape')).encode('ascii', 'ignore'),reviewer["accesskey"]))
                data["success"] = success
                print data
            else:
                print "nothing to do"
        #else:
        #    print type(abstracts[0]["submitter"]), type(userId)
        #is this the reviewer that will approve the abstract?
    return conference_abstract.util.generate_response(data)
