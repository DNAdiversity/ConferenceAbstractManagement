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
service = Service(name='abstractChair', path='/abstract/{abstractId}/chair',description=info_desc)

def getAbstractChairs(abstractId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    topics = []
    categories = []
    chairs = []
    topicChairs = []
    topicChairTemp = {}
    categoryChairs = []
    categoryChairTemp = {}
    categoryChairIDs = []
    reviewers = [0]
    try:
        sql = """select fk_reviewer from review_assignments where fk_abstracts=%s;"""
        cur.execute(sql,(abstractId,))
        reviewers = []
        if cur.rowcount > 0:
            for row in cur.fetchall():
                print row["fk_reviewer"]
                reviewers.append(row["fk_reviewer"])
        sql = """select selected_topics from abstracts where id=%s;"""
        print cur.mogrify(sql,(abstractId,))
        cur.execute(sql,(abstractId,))
        result = cur.fetchone()
        if len(result)>0:
            print result["selected_topics"]
            topics = result["selected_topics"][2:len(result["selected_topics"])-2].split("','")
            sqlCategories = "select distinct(category) from topics where label in ("+result["selected_topics"][1:len(result["selected_topics"])-1]+")"
            print sqlCategories
            cur.execute(sqlCategories)
            for row in cur.fetchall():
                #print row
                categories.append(row["category"])
        if len(topics)>0 or len(categories) > 0:
            for topic in topics:
                sql = "select * from chairs where topics ilike '%"+topic+"%'"
                print sql
                cur.execute(sql)
                for row in cur.fetchall():
                    print row["id"],row["fullname"]
                    if row["id"] not in chairs:
                        chairs.append(row["id"])
                        #topicChairs.append({"id":row["id"],"fullname":row["fullname"],"topics":row["topic"],"email":row["email"]})
                        topicChairTemp[row["id"]] = {"fullname":row["fullname"],"topics":topic,"email":row["email"]}
                    else:
                        #print "adding another one to "+str(row["id"])
                        topicChairTemp[row["id"]]["topics"] += ", "+topic
            #print "Now putting together"
            for chairID in topicChairTemp:
                row = topicChairTemp[chairID]
                topicChairs.append({"id":chairID,"fullname":row["fullname"],"topics":row["topics"],"email":row["email"]})
            for category in categories:
                sql = "select * from chairs where categories ilike '%"+category+"%'"
                print sql
                cur.execute(sql)
                for row in cur.fetchall():
                    print row["id"],row["fullname"],categoryChairs
                    if row["id"] not in chairs:
                        chairs.append(row["id"])
                        categoryChairIDs.append(row["id"])
                        #categoryChairs.append({"id":row["id"],"fullname":row["fullname"],"email":row["email"]})
                        categoryChairTemp[row["id"]] = {"fullname":row["fullname"],"categories":category,"email":row["email"]}
                    elif row["id"] in categoryChairIDs:
                        #we found another one in the category only list
                        #print "found another one for category chair ID:"+str(row["id"])
                        categoryChairTemp[row["id"]]["categories"] += ", "+category
            for chairID in categoryChairTemp:
                row = categoryChairTemp[chairID]
                categoryChairs.append({"id":chairID,"fullname":row["fullname"],"categories":row["categories"],"email":row["email"]})

    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return topicChairs,categoryChairs,reviewers

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
    topicChairs,categoryChairs,reviewers = getAbstractChairs(abstractId)
    if len(topicChairs)>0 or len(categoryChairs)>0:
        
        data["topicChairs"] = topicChairs
        data["categoryChairs"] = categoryChairs
        data["reviewer"] = reviewers
        data["success"] = True
    return conference_abstract.util.generate_response(data)
