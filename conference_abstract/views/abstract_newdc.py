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

info_desc = """\
This is the home page for brave
"""

service = Service(name='abstractNewdc', path='/abstractNewdc', description=info_desc)

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
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
    print getCategories()
    #time.sleep(5)
    categories, categoryNames = getCategories()
    templateVars = {
        "user":user,
        "request":request,
        "pageTitle":"",
        "pageDesc":"",
        "categories":categories,
        "categoryNames":categoryNames
    }
    return conference_abstract.util.generate_template('abstractNew.mako',templateVars)

@service.post()
def service_post(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
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
    
    print request.POST
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