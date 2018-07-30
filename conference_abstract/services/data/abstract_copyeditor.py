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
This will get the abstract copy editor info and all the copy editors
"""
service = Service(name='abstractCopyEditor', path='/abstract/{abstractId}/copyeditor',description=info_desc)

def getAbstractEditors(abstractId):
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    copyeditors = []
    editors = [0]
    try:
        sql = """select fk_copyeditor from editor_assignments where fk_abstracts=%s;"""
        cur.execute(sql,(abstractId,))
        editors = []
        if cur.rowcount > 0:
            for row in cur.fetchall():
                print row["fk_copyeditor"]
                editors.append(row["fk_copyeditor"])
        sql = """select * from copyeditors order by fullname"""
        print cur.mogrify(sql)
        cur.execute(sql)
        if cur.rowcount > 0:
            for row in cur.fetchall():
                copyeditors.append({"fullname":row["fullname"],"id":row["id"],"email":row["email"]})

    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
    return copyeditors,editors

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
    copyEditors,editors = getAbstractEditors(abstractId)
    if len(copyEditors)>0:
        
        data["copyEditors"] = copyEditors
        data["editors"] = editors
        data["success"] = True
    return conference_abstract.util.generate_response(data)
