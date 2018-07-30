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
from conference_abstract.services.data.abstract_info import getAbstract,getAbstractFullDetails,getAbstractFullDetailsUnicode,getAbstractHistory
from conference_abstract.services.data.abstract_chair import getAbstractChairs
from conference_abstract.services.data.abstract_copyeditor import getAbstractEditors
from conference_abstract.services.data.abstract_topics import getCategories as getAbstractCategories

info_desc = """\
This is the home page for brave
"""

service = Service(name='abstractCopyEdit', path='/abstractCopyEdit/{abstractId}', description=info_desc)

def getCategories():
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = """select * from topics order by category, label;"""
    categories = []
    categoryNames = []
    currentCategory = 0
    cur.execute(sql)
    for row in cur.fetchall():
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
    abstract = None
    abstractAuthors = None
    reviewer = 0
    templateVars = {
        'user':None,
        'breadCrumbs':None,
        'pageTitle':'',
        'pageDesc':''
    }
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
        templateVars["user"] = user
        if user.is_admin() or user.is_editor():
            abstractId = request.matchdict['abstractId']
            abstracts, authors = getAbstractFullDetailsUnicode(abstractId)
            #can any admin / chair go to the pages?
            if abstracts is not None and len(abstracts)>0:
                topicChairs,categoryChairs,reviewers = getAbstractChairs(abstractId)
                categories, categoryNames, selectedTopics = getAbstractCategories(abstractId)
                abstract = abstracts[0]
                abstractAuthors = authors[int(abstractId)]
                abstractHistory = getAbstractHistory(abstractId)
                editors, currentEditor = getAbstractEditors(abstractId)
                if len(currentEditor) == 0:
                    currentEditor = [0]
                reviewersAvailable = True
                if len(topicChairs) == 0 and len(categoryChairs) == 0:
                    reviewersAvailable = False
                return conference_abstract.util.generate_template('abstractCopyEdit.mako',{
                    'user': user,
                    'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Abstract Review"}],
                    'abstract':abstract,
                    'authors':abstractAuthors,
                    'reviewers': reviewers,
                    'reviewersAvailable':reviewersAvailable,
                    'categories':categories,
                    'categoryNames':categoryNames,
                    'selectedTopics':selectedTopics,
                    'abstractHistory':abstractHistory,
                    'editors':currentEditor,
                    'pageTitle':'',
                    'pageDesc':''
                })
            else:
                templateVars["user"] = user
                #no abstract found
                #check if it is a reviewer with thier access key and is also logged in
                pass
                return conference_abstract.util.generate_template('abstractNotFound.mako',templateVars)
        else:
            return conference_abstract.util.generate_template('noAccess.mako',templateVars)
    else:
        #check if it is a reviewer with thier access key.
        pass
    return conference_abstract.util.generate_template('noAccess.mako',templateVars)

@service.post()
def service_post(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    registrationSuccess = False
    abstractTitle = request.POST.get('abstractTitle', None)
    abstractText = request.POST.get('abstractText', None)
    abstractType = request.POST.get('abstractType', None)
    category = request.POST.getall('category[]')
    authorFirstnames = request.POST.getall('firstname[]')
    authorInitials = request.POST.getall('initial[]')
    authorLastnames = request.POST.getall('lastname[]')
    authorInstitutions = request.POST.getall('institution[]')
    authorEmail = request.POST.getall('email[]')
    authorCountries = request.POST.getall('country[]')
    authorPresenting = request.POST.getall('presenting[]')
    authorCorresponding = request.POST.getall('corresponding[]')
    
    debug = False
    
    print request.POST
    if debug == True:
        data = request.POST
        sqlList = []
        abstractId = 36
        conn = conference_abstract.util.get_connection()
        cur = conn.cursor()
        sql = """insert into authorship (fk_abstract, fname, mname, lname, corresponding, presenting, institution, country, email) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        for i in range(len(authorFirstnames)):
            if authorFirstnames[i] != "":
                try:
                    sqlOut = cur.mogrify ( sql,
                        (
                            abstractId,
                            authorFirstnames[i],
                            authorInitials[i],
                            authorLastnames[i],
                            authorCorresponding[i],
                            authorPresenting[i],
                            authorInstitutions[i],
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
        
        registrationSuccess = True
        conn = conference_abstract.util.get_connection()
        cur = conn.cursor()
        sql = """insert into abstracts (fk_submitter, title, abstract_text, selected_topics,submission_date,modification_date,abstract_type) values (%s, %s, %s, %s, now(),now(),%s) RETURNING id;"""
        print cur.mogrify( sql, 
            (userId, 
            abstractTitle.encode("ascii",errors='ignore'), 
            abstractText.encode("ascii",errors='ignore'), 
            "{"+",".join(category)+"}",abstractType,) )
        
        try:
            cur.execute( sql, 
                (userId, 
                abstractTitle, 
                abstractText, 
                "{"+",".join(category)+"}",abstractType,) )
            abstractId = cur.fetchone()[0]
            conn.commit()
            print abstractId
        except Exception as e:
            print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
            print e
            print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        if len(authorFirstnames) > 0:
            sql = """insert into authorship (fk_abstract, fname, mname, lname, corresponding, presenting, institution, country, email) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            for i in range(len(authorFirstnames)):
                try:
                    if authorFirstnames[i] != "" and authorLastnames[i] != "":
                        print cur.mogrify ( sql,
                            (abstractId,
                            authorFirstnames[i],
                            authorInitials[i],
                            authorLastnames[i],
                            authorCorresponding[i],
                            authorPresenting[i],
                            authorInstitutions[i],
                            authorCountries[i],
                            authorEmail[i],
                            )
                        )
                        cur.execute ( sql,
                            (abstractId,
                            authorFirstnames[i],
                            authorInitials[i],
                            authorLastnames[i],
                            authorCorresponding[i],
                            authorPresenting[i],
                            authorInstitutions[i],
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


