from cornice import Service
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
import pyramid.security
import uuid
import shutil

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
This is the attachment upload page
"""

service = Service(name='abstractAttachment', path='/abstract/{abstractId}/attachment', description=info_desc)


def isAbstractPoster(abstractId):
    authors = []
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = """select * from (
select * from 
(select abstracts.id, abstracts.title, abstract_type, abstract_text, abstract_text_edited, abstracts.abstract_attachment, authorlist.all_authors
from abstracts 
left join authorlist on authorlist.fk_abstract = abstracts.id
where abstract_type in ('Poster') and review_status = 'EDITED') as abstracts_to_join
union
(select abstracts.id, abstracts.title, abstract_type, abstract_text, abstract_text_edited, abstracts.abstract_attachment, authorlist.all_authors from agenda 
left join abstracts on agenda.fk_abstracts = abstracts.id
left join authorlist on authorlist.fk_abstract = abstracts.id
where abstracts.abstract_type = 'Lightning Talk'
) ) as available_abstracts
where available_abstracts.id=%s and abstract_attachment is null;""" # and abstract_attachment is null 
    cur.execute(sql,[str(abstractId)])
    if cur.rowcount < 1:
        return False
    else:
        row = cur.fetchone()
        abstract = {
            "id"    : row["id"],
            "title" : row["title"],
            "abstract_type" : row["abstract_type"],
            "authors" : row["all_authors"],
            "attachment" : row["abstract_attachment"]
        }
        if row["abstract_text_edited"] is not None:
            abstract["abstract_text_edited"] = row["abstract_text_edited"]
        else:
            abstract["abstract_text_edited"] = row["abstract_text"]
    return abstract

def isAbstractPosterLoggedIn(abstractId,submitterId):
    authors = []
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = """select * from (
select * from 
(select abstracts.id, abstracts.title, abstract_type, abstract_text, abstract_text_edited, abstracts.abstract_attachment, authorlist.all_authors, abstracts.fk_submitter
from abstracts 
left join authorlist on authorlist.fk_abstract = abstracts.id
where abstract_type in ('Poster') and review_status = 'EDITED') as test
union
(select abstracts.id, abstracts.title, abstract_type, abstract_text, abstract_text_edited, abstracts.abstract_attachment, authorlist.all_authors, abstracts.fk_submitter from agenda 
left join abstracts on agenda.fk_abstracts = abstracts.id
left join authorlist on authorlist.fk_abstract = abstracts.id
where abstracts.abstract_type = 'Lightning Talk'
) ) as available_abstracts
where available_abstracts.id=%s and available_abstracts.fk_submitter = %s and abstract_attachment is null;""" #  
    cur.execute(sql,[abstractId,submitterId])
    if cur.rowcount < 1:
        return False
    else:
        row = cur.fetchone()
        abstract = {
            "id"    : row["id"],
            "title" : row["title"],
            "abstract_type" : row["abstract_type"],
            "authors" : row["all_authors"],
            "attachment" : row["abstract_attachment"]
        }
        if row["abstract_text_edited"] is not None:
            abstract["abstract_text_edited"] = row["abstract_text_edited"]
        else:
            abstract["abstract_text_edited"] = row["abstract_text"]
    return abstract


def decodeID(abstractIdTemp):
    abstractId = int(float("%.17g" % abstractIdTemp)/1234567890*3.1415)
    print "*******>>>******"
    print abstractId,("%.17g" % abstractIdTemp)
    print "*******>>>******"
    #need to rounding to 15 places to make sure this is the correct one.
    if abstractId == float("%.13g" % (float("%.17g" % abstractIdTemp)/1234567890*3.1415)):
        return abstractId
    else:
        return 0

def encodeID(abstractID):
    return (abstractId/3.1415*1234567890)

@service.get()
def service_get(request):
    user = None
    abstract = None
    abstractAuthors = None
    reviewer = 0
    templateVars = {
        'user':None,
        'breadCrumbs':None,
        'pageTitle':'',
        'pageDesc':''
    }
    login = pyramid.security.authenticated_userid(request)
    user = None
    userId = 0
    if login is not None:
        user = conference_abstract.auth.check_user(request)
    if user == False or user == None:
        abstractIdEncoded = float("%.17g" % float(request.matchdict['abstractId']))
        idFix = {'307708628957.50433':783,'280199556126.05438':713,'334038741524.74927':850,'323428099146.9043':823,'155622754875.05966':396,'325000046165.8443':827,'169770278045.51962':432,'304171748164.88934':774,'87636046305.904816':223,'326964979939.51929':832,'176058066121.2796':448,'321463165373.22931':818,'163482489969.75964':416,'297490973334.39435':757,'297097986579.65936':756,'157194701893.99966':400,'166233397252.90463':423,'190598576046.47458':485,'279806569371.3194':712,'314389403787.99933':800}
        if request.matchdict['abstractId'] in idFix:
            abstractId = idFix[request.matchdict['abstractId']]
        else:
            abstractId = decodeID(abstractIdEncoded)
        abstract = isAbstractPoster(abstractId)
    else:
        abstractId = request.matchdict['abstractId']
        abstractIdEncoded = abstractId
        userObj = user.get_userObj()
        user.check_userLevel()
        abstract = isAbstractPosterLoggedIn(abstractId, userObj["userId"])
    #abstractIdEncoded = request.matchdict['abstractId']
    #abstractId = request.matchdict['abstractId']
    #print abstract
    if abstract is not False:
        if abstract["attachment"] is not None:
            templateVars = {
                "user": user,
                "title": "Abstract Updated",
                "message": "This abstract already has a poster uploaded. Please contact <a href='mailto:abstract@ibol.org'>abstract@ibol.org</a> if you want to replace it."
            }
            return conference_abstract.util.generate_template('abstractThankYouMessage.mako',templateVars)
        else:
            return conference_abstract.util.generate_template('abstractAttachment.mako',{
                'user': user,
                'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Abstract "}],
                'abstract':abstract,
                'abstractIdEncoded':abstractIdEncoded,
                'pageTitle':'',
                'pageDesc':'',
                'request':request 
            })
    else:
        templateVars["user"] = user
        return conference_abstract.util.generate_template('abstractNotFound.mako',templateVars)
    return conference_abstract.util.generate_template('noAccess.mako',templateVars)

@service.post()
def service_post(request):
    #Notes: Only can submit successful if nothing there already
    #record the ip address
    user = None
    success = False
    data = {"success":False}
    abstractIdEncoded = request.matchdict['abstractId']
    login = pyramid.security.authenticated_userid(request)
    user = None
    userId = 0
    if login is not None:
        user = conference_abstract.auth.check_user(request)
    if user == False or user == None:
        abstractIdEncoded = float("%.17g" % float(request.matchdict['abstractId']))
        idFix = {'307708628957.50433':783,'280199556126.05438':713,'334038741524.74927':850,'323428099146.9043':823,'155622754875.05966':396,'325000046165.8443':827,'169770278045.51962':432,'304171748164.88934':774,'87636046305.904816':223,'326964979939.51929':832,'176058066121.2796':448,'321463165373.22931':818,'163482489969.75964':416,'297490973334.39435':757,'297097986579.65936':756,'157194701893.99966':400,'166233397252.90463':423,'190598576046.47458':485,'279806569371.3194':712,'314389403787.99933':800}
        if request.matchdict['abstractId'] in idFix:
            abstractId = idFix[request.matchdict['abstractId']]
        else:
            abstractId = decodeID(abstractIdEncoded)
        abstract = isAbstractPoster(abstractId)
    else:
        abstractId = request.matchdict['abstractId']
        abstractIdEncoded = abstractId
        userObj = user.get_userObj()
        user.check_userLevel()
        abstract = isAbstractPosterLoggedIn(abstractId, userObj["userId"])
    if abstract is not False:
        try:
            print request.POST['abstractAttachment'].filename
            filename = request.POST['abstractAttachment'].filename
            parseFilename = filename.rsplit(".",1)
            if len(parseFilename) == 2:
                if parseFilename[1].lower() == "pdf":
                    input_file = request.POST['abstractAttachment'].file
                    input_file.seek(0)
                    file_path = os.path.join('/var/www/attachments', '%s.pdf' % abstractId)
                    temp_file_path = file_path + '~'
                    with open(temp_file_path, 'wb') as output_file:
                        shutil.copyfileobj(input_file, output_file)
                    os.rename(temp_file_path, file_path)
                    success = True
        except Exception as e:
            print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
            print e
            print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
            return conference_abstract.util.generate_response(data)
            #return conference_abstract.util.generate_template('error.mako',{"user":user,"request":request})
    print success,abstract
    if success == True:
        conn = conference_abstract.util.get_connection()
        cur = conn.cursor()
        sql = """update abstracts set abstract_attachment = true where abstracts.id = %s RETURNING id;"""
        print cur.mogrify(sql,[abstractId])
        try:
            cur.execute(sql,[abstractId])
            if cur.rowcount == 1:
                result = cur.fetchone()
                data = {"success":True}
                conn.commit()
            nowTime = str(datetime.datetime.now())
            logFile = open("/tmp/upload.log","a")
            logFile.write(nowTime+"\t"+str(result)+"\t"+str(abstractId)+"\t"+str(request.client_addr)+"\n")
            logFile.close();
            templateVars = {
                "user": user,
                "title": "Abstract Upload Complete",
                "message": "Thank you for uploading your poster"
            }
            return conference_abstract.util.generate_template('abstractPosterMessage.mako',templateVars)
        except Exception as e:
            print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
            print e
            print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        conn.close()
    else:
        templateVars = {
            "user": user,
            "title": "Abstract Upload Error",
            "message": "The server ran into an error. Please try uploading your poster at a later time."
        }
        return conference_abstract.util.generate_template('abstractPosterMessage.mako',templateVars)
    return conference_abstract.util.generate_response(data)


