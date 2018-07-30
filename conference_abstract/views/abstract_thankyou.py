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
import unicodedata

info_desc = """\
This is the home page for brave
"""

service = Service(name='abstractThankyou', path='/abstract/{abstractId}/ThankYou', description=info_desc)

def isAbstractInAgenda(abstractId):
    authors = []
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = """select agenda.*, abstracts.title, abstract_type, abstract_text_edited from agenda left join abstracts on agenda.fk_abstracts = abstracts.id where abstracts.id = %s;"""
    cur.execute(sql,[abstractId])
    if cur.rowcount != 1:
        return False,False
    else:
        row = cur.fetchone()
        abstract = {
            "id"    : row["fk_abstracts"],
            "title" : unicodedata.normalize('NFKD', row["title"].decode('unicode-escape')).encode('ascii', 'ignore'),
            "abstract_type"  : row["abstract_type"],
            "abstract_text_edited"  : unicodedata.normalize('NFKD', row["abstract_text_edited"].decode('unicode-escape')).encode('ascii', 'ignore')
        }
        sqlAuthor = """select fk_abstract, fname || ' ' || mname || ' ' || lname as fullname, fname, mname, lname, corresponding, presenting, institution, department, address, country, email, id from authorship where fk_abstract=%s order by id asc"""
        print cur.mogrify(sqlAuthor,(abstractId,))
        cur.execute(sqlAuthor,(abstractId,))
        for row in cur.fetchall():
            abstractId = row["fk_abstract"]
            print "working on :",abstractId
            ##if abstractId not in authors:
            ##    authors[abstractId] = []
            ##authors[abstractId].append({
            authors.append({
                "id":row["id"],
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
    return abstract, authors

def decodeID(abstractIdTemp):
    abstractId = int(abstractIdTemp/1234567890*3.1415)
    return abstractId

def encodeID(abstractID):
    return (abstractId/3.1415*1234567890)

@service.get()
def service_get(request):
    #login = pyramid.security.authenticated_userid(request)
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
    #abstractIdEncoded = request.matchdict['abstractId']
    #abstractId = decodeID(float(abstractIdEncoded))
    #abstract, authors = isAbstractInAgenda(abstractId)
    return conference_abstract.util.generate_template('abstractThankYou.mako',{
        'user': user,
        'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Abstract "}],
        'pageTitle':'',
        'pageDesc':'',
        'request':request 
    })

