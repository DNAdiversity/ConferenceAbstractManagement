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
from conference_abstract.services.data.abstract_info import getAbstract
import unicodedata

info_desc = """\
This is the home page for brave
"""

service = Service(name='abstractNew', path='/abstractNew', description=info_desc)

def getCategories():
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = """select * from topics order by category, label;"""
    categories = []
    categoryNames = []
    currentCategory = 0
    cur.execute(sql)
    for row in cur:
        categoryName = row['category']
        if categoryName not in categoryNames:
            currentCategory = len(categoryNames)
            categoryNames.append(categoryName)
            categories.append([])
        categories[currentCategory].append({"id":row["id"],"label":row["label"]})
    conn.close()
    return categories, categoryNames

@service.get()
def service_get(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    templateVars = {
        "user":user,
        "request":request,
        "pageTitle":"",
        "pageDesc":"",
    }
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
        print getCategories()
        #time.sleep(5)
        categories, categoryNames = getCategories()
        templateVars["user"]=user
        templateVars["categories"]=categories
        templateVars["categoryNames"]=categoryNames
        return conference_abstract.util.generate_template('abstractNew.mako',templateVars)
    else:
        return conference_abstract.util.generate_template('noAccess.mako',{"user":None})


@service.post()
def service_post(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    originalAbstractId = request.POST.get('abstractId',0)
    abstractTitle = request.POST.get('abstractTitle', None)
    abstractText = request.POST.get('abstractText', None)
    abstractType = request.POST.get('abstractType', None)
    category = request.POST.getall('category[]')
    authorFirstnames = request.POST.getall('firstname[]')
    authorInitials = request.POST.getall('initial[]')
    authorLastnames = request.POST.getall('lastname[]')
    authorInstitutions = request.POST.getall('institution[]')
    authorDepartments = request.POST.getall('department[]')
    authorAddresses = request.POST.getall('address[]')
    authorEmail = request.POST.getall('email[]')
    authorCountries = request.POST.getall('country[]')
    authorPresenting = request.POST.getall('presenting[]')
    authorCorresponding = request.POST.getall('corresponding[]')
    abstractId = None
    debug = False
    
    print request.POST
    if debug == True:
        data = request.POST
        sqlList = []
        abstractId = 36
        conn = conference_abstract.util.get_connection()
        cur = conn.cursor()
        sql = """insert into abstracts (fk_submitter, title, abstract_text, selected_topics,submission_date,modification_date,abstract_type) values (%s, %s, %s, %s, now(),now(),%s) RETURNING id;"""
        sqlList.append( cur.mogrify( sql, 
            (userId, 
            unicodedata.normalize('NFKD', abstractTitle).encode('ascii', 'ignore'),
            unicodedata.normalize('NFKD', abstractText).encode('ascii', 'ignore'),
            "{"+",".join(category)+"}",abstractType,) )
        )
        sql = """insert into authorship (fk_abstract, fname, mname, lname, corresponding, presenting, institution, department, address, country, email) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        for i in range(len(authorFirstnames)):
            if authorFirstnames[i] != "":
                try:
                    sqlOut = cur.mogrify ( sql,
                        (
                            abstractId,
                            unicodedata.normalize('NFKD', authorFirstnames[i]).encode('ascii', 'ignore'),
                            unicodedata.normalize('NFKD', authorInitials[i]).encode('ascii', 'ignore'),
                            unicodedata.normalize('NFKD', authorLastnames[i]).encode('ascii', 'ignore'),
                            authorCorresponding[i],
                            authorPresenting[i],
                            unicodedata.normalize('NFKD', authorInstitutions[i]).encode('ascii', 'ignore'),
                            unicodedata.normalize('NFKD', authorDepartments[i]).encode('ascii', 'ignore'),
                            unicodedata.normalize('NFKD', authorAddresses[i]).encode('ascii', 'ignore'),
                            authorCountries[i],
                            authorEmail[i],
                        ))
                    print sqlOut
                    sqlList.append(sqlOut)
                except Exception as e:
                    print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
                    print e
                    print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"

        data["sql"] = sqlList
        return conference_abstract.util.generate_response(conference_abstract.util.jsonify(data))
    if login is not None:
        loginParse = login.split("|")
        username = loginParse[0]
        userId = loginParse[1]
        user = conference_abstract.auth.check_user(request)
    print abstractTitle, abstractText, category
    if abstractTitle != "" and abstractText != "" and category != "":
        
        conn = conference_abstract.util.get_connection()
        cur = conn.cursor()
        sqlDeleteAuthorship = """delete from authorship where fk_abstract = %s"""
        sqlDelete = """delete from abstracts where id = %s"""
        sql = """insert into abstracts (fk_submitter, title, abstract_text, selected_topics,submission_date,modification_date,abstract_type) values (%s, %s, %s, %s, now(),now(),%s) RETURNING id;"""
        #print cur.mogrify( sql, 
        #    (userId, 
        #    unicodedata.normalize('NFKD', abstractTitle).encode('ascii', 'ignore'),
        #    unicodedata.normalize('NFKD', abstractText).encode('ascii', 'ignore'),
        #    "{"+",".join(category)+"}",abstractType,) )
        
        try:
            cur.execute( sqlDeleteAuthorship, (originalAbstractId,))
            cur.execute( sqlDelete, (originalAbstractId,))
            conn.commit();
            cur.execute( sql, 
                (userId, 
                #unicodedata.normalize('NFKD', abstractTitle).encode('ascii', 'ignore'),
                #unicodedata.normalize('NFKD', abstractText).encode('ascii', 'ignore'),
                abstractTitle,
                abstractText,
                "{"+",".join(category)+"}",abstractType,) )
            abstractId = cur.fetchone()[0]
            
            #cur.execute("insert into stats_and_dates (registered_participants, abstracts_received, conference_date, abstracts_deadline,seats_available)  (select registered_participants, abstracts_received+1, conference_date, abstracts_deadline,seats_available from stats_and_dates order by id desc limit 1)")
            conn.commit()
            print abstractId
        except Exception as e:
            print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
            print e
            print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        if len(authorFirstnames) > 0:
            sql = """insert into authorship (fk_abstract, fname, mname, lname, corresponding, presenting, institution, department, address, country, email) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            for i in range(len(authorFirstnames)):
                try:
                    if authorFirstnames[i] != "" and authorLastnames[i] != "":
                        #print cur.mogrify ( sql,
                        #    (abstractId,
                        #    #unicodedata.normalize('NFKD', authorFirstnames[i]).encode('ascii', 'ignore'),
                        #    #unicodedata.normalize('NFKD', authorInitials[i]).encode('ascii', 'ignore'),
                        #    #unicodedata.normalize('NFKD', authorLastnames[i]).encode('ascii', 'ignore'),
                        #    unicodedata.normalize('NFKD', authorFirstnames[i]).encode('ascii', 'ignore'),
                        #    unicodedata.normalize('NFKD', authorInitials[i]).encode('ascii', 'ignore'),
                        #    unicodedata.normalize('NFKD', authorLastnames[i]).encode('ascii', 'ignore'),
                        #    authorCorresponding[i],
                        #    authorPresenting[i],
                        #    unicodedata.normalize('NFKD', authorInstitutions[i]).encode('ascii', 'ignore'),
                        #    authorCountries[i],
                        #    authorEmail[i],
                        #    )
                        #)
                        cur.execute ( sql,
                            (abstractId,
                            #unicodedata.normalize('NFKD', authorFirstnames[i]).encode('ascii', 'ignore'),
                            #unicodedata.normalize('NFKD', authorInitials[i]).encode('ascii', 'ignore'),
                            #unicodedata.normalize('NFKD', authorLastnames[i]).encode('ascii', 'ignore'),
                            authorFirstnames[i],
                            authorInitials[i],
                            authorLastnames[i],
                            authorCorresponding[i],
                            authorPresenting[i],
                            #unicodedata.normalize('NFKD', authorInstitutions[i]).encode('ascii', 'ignore'),
                            authorInstitutions[i],
                            authorDepartments[i],
                            authorAddresses[i],
                            authorCountries[i],
                            authorEmail[i],
                            )
                        )
                        conn.commit()
                    
                except Exception as e:
                    print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
                    print e
                    print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
                    
        #print "sleeping ....zzzzZZZZ"
        #time.sleep(5)
        #print "done sleep"
        
        #print userId[0]
        
        abstracts, authors = getAbstract(abstractId)
        abstract = None
        abstractAuthors = None
        if abstracts is not None and len(abstracts)>0:
            abstract = abstracts[0]
            abstractAuthors = authors[int(abstractId)]

        return conference_abstract.util.generate_template('abstractSubmit.mako',{
            'user': user,
            'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Abstract Submission"}],
            'abstract':abstract,
            'authors':abstractAuthors,
            'pageTitle':'',
            'pageDesc':''
        })
        #return conference_abstract.util.generate_template('registrationSuccess.mako',templateVars)
    else:
        categories, categoryNames = getCategories()
        templateVars = {
            'message':'',
            'user': user,
            'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Abstract Submission"}],
            'pageTitle':'',
            'pageDesc':'',
            "categories":categories,
            "categoryNames":categoryNames,
            "request":request
        }
        templateVars["formData"] = request.POST
        return conference_abstract.util.generate_template('abstractNew.mako',templateVars)


