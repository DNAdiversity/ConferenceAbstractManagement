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
service = Service(name='abstractInfo', path='/abstract/{abstractId}',description=info_desc)

def getAbstract(abstractId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    abstracts = []
    authors = {}
    currentCategory = 0
    try:
        sql = """select abstracts.id, title, submission_date, abstract_text, selected_topics, abstract_type, review_status, cusers.salutation || ' ' || cusers.first_name || ' ' || cusers.middle_initial || ' ' || cusers.last_name as submitter_name from abstracts left join cusers on abstracts.fk_submitter = cusers.id where abstracts.id=%s """
        print cur.mogrify(sql,(abstractId,))
        cur.execute(sql,(abstractId,))
        for row in cur.fetchall():
            abstracts.append({"id":row["id"],"title":unicodedata.normalize('NFKD', row["title"].decode('unicode-escape')).encode('ascii', 'ignore'),"submission_date":row["submission_date"].strftime('%Y/%m/%d %H:%M'),"review_status":row["review_status"],"submitter_name":unicodedata.normalize('NFKD', row["submitter_name"].decode('unicode-escape')).encode('ascii', 'ignore'),"abstract_text":unicodedata.normalize('NFKD', row["abstract_text"].decode('unicode-escape')).encode('ascii', 'ignore'),"abstract_type":row["abstract_type"],"categories":row["selected_topics"]})
        sqlAuthor = """select fk_abstract, fname || ' ' || mname || ' ' || lname as fullname from authorship where fk_abstract=%s order by id asc"""
        print cur.mogrify(sqlAuthor,(abstractId,))
        cur.execute(sqlAuthor,(abstractId,))
        for row in cur.fetchall():
            abstractId = row["fk_abstract"]
            if abstractId not in authors:
                authors[abstractId] = []
            authors[abstractId].append(unicodedata.normalize('NFKD', row["fullname"].decode('unicode-escape')).encode('ascii', 'ignore'))
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return abstracts,authors

def getAbstractFullDetails(abstractId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    abstracts = []
    authors = {}
    currentCategory = 0
    try:
        sql = """select abstracts.id, title, submission_date, abstract_text, selected_topics, abstract_type, review_status, cusers.salutation || ' ' || cusers.first_name || ' ' || cusers.middle_initial || ' ' || cusers.last_name as submitter_name, fk_submitter from abstracts left join cusers on abstracts.fk_submitter = cusers.id where abstracts.id=%s """
        print cur.mogrify(sql,(abstractId,))
        cur.execute(sql,(abstractId,))
        for row in cur.fetchall():
            abstracts.append({"id":row["id"],"title":unicodedata.normalize('NFKD', row["title"].decode('unicode-escape')).encode('ascii', 'ignore'),"submission_date":row["submission_date"].strftime('%Y/%m/%d %H:%M'),"review_status":row["review_status"],"submitter_name":unicodedata.normalize('NFKD', row["submitter_name"].decode('unicode-escape')).encode('ascii', 'ignore'),"abstract_text":unicodedata.normalize('NFKD', row["abstract_text"].decode('unicode-escape')).encode('ascii', 'ignore'),"abstract_type":row["abstract_type"],"categories":row["selected_topics"],"submitter":row["fk_submitter"]})
        sqlAuthor = """select fk_abstract, fname || ' ' || mname || ' ' || lname as fullname, fname, mname, lname, corresponding, presenting, institution, department, address, country, email from authorship where fk_abstract=%s order by id asc"""
        print cur.mogrify(sqlAuthor,(abstractId,))
        cur.execute(sqlAuthor,(abstractId,))
        for row in cur.fetchall():
            abstractId = row["fk_abstract"]
            print "working on :",abstractId
            if abstractId not in authors:
                authors[abstractId] = []
            authors[abstractId].append({
                "fullname":unicodedata.normalize('NFKD', row["fullname"].decode('unicode-escape')).encode('ascii', 'ignore'),
                "first_name":unicodedata.normalize('NFKD', row["fname"].decode('unicode-escape')).encode('ascii', 'ignore'),
                "middle_initial":unicodedata.normalize('NFKD', row["mname"].decode('unicode-escape')).encode('ascii', 'ignore'),
                "last_name":unicodedata.normalize('NFKD', row["lname"].decode('unicode-escape')).encode('ascii', 'ignore'),
                "corresponding":row["corresponding"],
                "presenting":row["presenting"],
                "institution":unicodedata.normalize('NFKD', row["institution"].decode('unicode-escape')).encode('ascii', 'ignore'),
                "department":unicodedata.normalize('NFKD', row["department"].decode('unicode-escape')).encode('ascii', 'ignore'),
                "address":unicodedata.normalize('NFKD', row["address"].decode('unicode-escape')).encode('ascii', 'ignore'),
                "country":row["country"],
                "email":row["email"]})
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return abstracts,authors

def getAbstractFullDetailsUnicode(abstractId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    abstracts = []
    authors = {}
    currentCategory = 0
    try:
        sql = """select abstracts.id, title, submission_date, abstract_text, 
        (
        CASE WHEN abstract_text_edited IS NOT NULL
            THEN abstract_text_edited
            ELSE ''
        END
        ) as abstract_text_edited,
        selected_topics, abstract_type, review_status, cusers.salutation || ' ' || cusers.first_name || ' ' || cusers.middle_initial || ' ' || cusers.last_name as submitter_name, fk_submitter from abstracts left join cusers on abstracts.fk_submitter = cusers.id where abstracts.id = %s """
        print cur.mogrify(sql,(abstractId,))
        cur.execute(sql,(abstractId,))
        for row in cur.fetchall():
            abstracts.append({"id":row["id"],"title":row["title"],"submission_date":row["submission_date"].strftime('%Y/%m/%d %H:%M'),"review_status":row["review_status"],"submitter_name":row["submitter_name"],"abstract_text":row["abstract_text"],"abstract_type":row["abstract_type"],"categories":row["selected_topics"],"submitter":row["fk_submitter"],"abstract_text_edited":row["abstract_text_edited"]})
        sqlAuthor = """select fk_abstract, fname || ' ' || mname || ' ' || lname as fullname, fname, mname, lname, corresponding, presenting, institution, department, address, country, email from authorship where fk_abstract=%s order by id asc"""
        print cur.mogrify(sqlAuthor,(abstractId,))
        cur.execute(sqlAuthor,(abstractId,))
        for row in cur.fetchall():
            abstractId = row["fk_abstract"]
            print "working on :",abstractId
            if abstractId not in authors:
                authors[abstractId] = []
            authors[abstractId].append({
                "fullname":row["fullname"],
                "first_name":row["fname"],
                "middle_initial":row["mname"],
                "last_name":row["lname"],
                "corresponding":row["corresponding"],
                "presenting":row["presenting"],
                "institution":row["institution"],
                "department":row["department"],
                "address":row["address"],
                "country":row["country"],
                "email":row["email"]})
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return abstracts,authors

def getAbstractHistory(abstractId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    history = []
    try:
        sql = """select score, suggested_topic, case notes when notes then notes else '' END as notes, score_date, chairs.fullname, chairs.email, topics.label, topics.category from abstracts_score 
        left join chairs on abstracts_score.fk_reviewer = chairs.id
        left join topics on abstracts_score.suggested_topic = topics.id
        where fk_abstracts = %s order by score_date desc;
        """
        print cur.mogrify(sql,[abstractId])
        cur.execute(sql,[abstractId])
        for row in cur.fetchall():
            history.append({"score":row["score"],"topicId":row["suggested_topic"],"notes":unicodedata.normalize('NFKD', row["notes"].decode('utf-8')).encode('ascii', 'ignore'),"scoreDate":row["score_date"].strftime('%Y/%m/%d %H:%M'),"reviewerEmail":row["email"],"reviewerFullname":unicodedata.normalize('NFKD', row["fullname"].decode('utf-8')).encode('ascii', 'ignore'),"topic":row["label"],"category":row["category"]})
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return history
    
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
    abstracts,authors = getAbstract(abstractId)
    if abstracts is not None and len(abstracts)>0:
        data["abstract"] = abstracts[0]
        data["authors"] = authors[int(abstractId)]
        data["success"] = True
    return conference_abstract.util.generate_response(data)
