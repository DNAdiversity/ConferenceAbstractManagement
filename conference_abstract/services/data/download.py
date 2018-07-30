from cornice import Service
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
import pyramid.security
from pyramid.response import Response

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
service = Service(name='download', path='/download',description=info_desc)

def getData():
    conn = conference_abstract.util.get_connection()
    #cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur = conn.cursor()
    columnLabels = ["column1","column2"]
    rows = []
    try:
        sql = """select selected_topics, review_status from abstracts where abstracts.review_status != 'UNSUBMITTED' """
        print cur.mogrify(sql)
        cur.execute(sql)
        if cur.rowcount > 0:
            for row in cur.fetchall():
                rows.append(row)
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        success = False
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"

    conn.close()
    return columnLabels, rows


@service.get()
def data_get(request):
    #allowed = pyramid.security.authenticated_userid(request)
    #if allowed is None:
    #    raise HTTPForbidden()
    data = ""
    columnLabels, rows = getData()
    if len(rows)>0:
        for column in columnLabels:
            data += column+"\t"
        data += "\n"
        for row in rows:
            for col in row:
                data += col+"\t"
            data += "\n"
    resp = Response()
    resp.body = str(data)
    #application/vnd.ms-excel
    resp.headers['Content-Disposition'] = 'attachment;filename="download.csv"'
    resp.headers['Content-type'] = 'text/csv'
    resp.headers['Expires'] = time.strftime("%d %m %Y %H:%M:%S")+ " EST"

    resp.content_type = 'text/csv; charset=utf-8'
    return resp
