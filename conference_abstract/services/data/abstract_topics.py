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
This will get the abstract info
"""
service = Service(name='abstractTopics', path='/abstract/{abstractId}/topics',description=info_desc)

def getCategories(abstractId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    selectedTopics = []
    try:
        sql = """select selected_topics, review_status from abstracts where abstracts.id=%s """
        print cur.mogrify(sql,(abstractId,))
        cur.execute(sql,(abstractId,))
        if cur.rowcount == 1:
            results = cur.fetchone()
            selectedTopics =  results["selected_topics"][2:len(results["selected_topics"])-2].split("','")
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        success = False
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"

    sql = """select * from topics order by category, label;"""
    categories = []
    categoryNames = []
    selectedTopicsInfo = []
    currentCategory = 0
    cur.execute(sql)
    for row in cur:
        categoryName = row['category']
        if categoryName not in categoryNames:
            currentCategory = len(categoryNames)
            categoryNames.append(categoryName)
            categories.append([])
        if row["label"] not in selectedTopics:
            categories[currentCategory].append({"id":row["id"],"label":row["label"]})
        else:
            selectedTopicsInfo.append({"id":row["id"],"label":row["label"]})
    conn.close()
    return categories, categoryNames, selectedTopicsInfo


@service.get()
def data_get(request):
    #allowed = pyramid.security.authenticated_userid(request)
    #if allowed is None:
    #    raise HTTPForbidden()
    data = {
        'success': False,
    }
    params = request.GET
    abstractId = request.matchdict['abstractId']
    categories, categoryNames, selectedTopics = getCategories(abstractId)
    if len(categories)>0:
        data["categories"] = categories
        data["categoryNames"] = categoryNames
        data["selectedTopics"] = selectedTopics
        data["success"] = True
    return conference_abstract.util.generate_response(data)
