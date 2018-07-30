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
service = Service(name='abstractAssignEditor', path='/abstract/{abstractId}/assignEditor',description=info_desc)

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

def assignAbstractEditor(abstractId,copyEditorId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    success = True
    try:
        sql = """insert into editor_assignments (fk_abstracts, fk_copyeditor, assigned_date) values (%s, %s, now()) RETURNING id;"""
        print cur.mogrify(sql,(abstractId,copyEditorId,))
        cur.execute(sql,(abstractId,copyEditorId,))
        #result = cur.fetchone()
        #print result
        sqlAbstractUpdate = """ update abstracts set modification_date = now(), review_status = %s where abstracts.id = %s"""
        print cur.mogrify(sqlAbstractUpdate,('ASSIGNED FOR EDIT', abstractId,))
        cur.execute(sqlAbstractUpdate,('ASSIGNED FOR EDIT', abstractId,))
        #result = cur.rowcount
        
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
            if result > 0:
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
            data["canIAssign"] = success
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
            print "I should assign"
            success = assignAbstractEditor(abstractId,copyEditorId)
            #success = True
            if success == True:
                #send and email
                abstract = getAbstract(abstractId)
                print "I assigned to ",editor["fullname"]
                mailTo = [editor["email"]]
                mailFrom = "abstracts@ibol.org"
                mailSubject = "iBOL 2017 abstract copy edit assignment notice - Automated Email"
                mailBody = """Dear Dr. %s,

Thank you for consenting to copy-edit abstracts for the 7th International Barcode of Life Conference.  We are writing to invite you to copy-edit an abstract that has been submitted.  The organizing committee would greatly appreciate your time in editing the submission. Please click the link below to access the editing dashboard on the conference abstract management system.  Once there, you will be able to edit the abstract directly.  If you are unable to copy edit the abstract, please respond to this email indicating so.

Submission to Edit:
Title: %s
Authors: %s
Abstract: 

%s


To perform edits or pass it to another copy editor, click on the following link:
http://abstracts.dnabarcodes2017.org/loginEditor/%s

If you would prefer to be removed from our copy edit list, please email abstracts@ibol.org

Thank you,
Conference Operating Committee
http://dnabarcodes2017.org/

"""

                conference_abstract.util.sendMail(mailFrom,mailTo,mailSubject,mailBody % (editor["fullname"],unicodedata.normalize('NFKD', abstract[0]["title"].decode('unicode-escape')).encode('ascii', 'ignore'),unicodedata.normalize('NFKD', abstract[0]["authors"].decode('unicode-escape')).encode('ascii', 'ignore'),unicodedata.normalize('NFKD', abstract[0]["text"].decode('unicode-escape')).encode('ascii', 'ignore'),editor["accesskey"]))
                data["success"] = success
                print data
            else:
                print "nothing to do"
        #else:
        #    print type(abstracts[0]["submitter"]), type(userId)
        #is this the editor that will approve the abstract?
    return conference_abstract.util.generate_response(data)
