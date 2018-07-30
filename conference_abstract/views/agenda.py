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
import unicodedata

info_desc = """\
This is the agenda for the conference
"""

service = Service(name='agenda', path='/agenda', description=info_desc)

@service.get()
def service_get(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    agendas = []
    authors = {}
    try:
        sql = """select agenda.*, abstracts.title, abstracts.abstract_text, abstract_type, abstract_text_edited, authorlist.all_authors, fk_authorship, agenda.chair from agenda left join abstracts on agenda.fk_abstracts = abstracts.id left join authorlist on authorlist.fk_abstract = abstracts.id left join abstracts_presenting on abstracts_presenting.fk_abstracts = abstracts.id order by agenda.date_time, agenda.room_name, agenda.session_order;"""
        print cur.mogrify(sql)
        cur.execute(sql)
        for row in cur.fetchall():
            abstractTitle = ""
            abstractType = ""
            abstractId = None
            abstractText = ""
            abstractTextEdited = ""
            if row["fk_abstracts"] is not None:
                if row["title"] is not None:
                    abstractTitle = row["title"]
                abstractType = row["abstract_type"]
                abstractId = row["fk_abstracts"]
                if row["abstract_text"] is not None:
                    abstractText = unicodedata.normalize('NFKD', row["abstract_text"].decode('unicode-escape')).encode('ascii', 'ignore')
                if row["abstract_text_edited"] is not None:
                    abstractTextEdited = unicodedata.normalize('NFKD', row["abstract_text_edited"].decode('unicode-escape')).encode('ascii', 'ignore')
            agendas.append({
                "id":row["id"],
                "session_id":row["session_id"],
                "session_name":row["session_name"],
                "room_name":row["room_name"],
                "date_time":row["date_time"],
                "session_order":row["session_order"],
                "abstract_type":abstractType,
                "abstract_id":abstractId,
                "title": abstractTitle,
                "abstract_text":abstractText,
                "abstract_text_edited":abstractTextEdited,
                "authors":row["all_authors"],
                "presenter_id":row["fk_authorship"],
                "chair":row["chair"]
            })
        
        sqlAuthor = """select fk_abstract, replace(fname || ' ' || mname || ' ' || lname,'  ',' ') as fullname, email, id, corresponding from authorship order by id;"""
        print cur.mogrify(sqlAuthor)
        cur.execute(sqlAuthor)
        for row in cur.fetchall():
            abstractId = row["fk_abstract"]
            if abstractId not in authors:
                authors[abstractId] = []
            authors[abstractId].append({"id":row["id"],"fullname":row["fullname"],"email":row["email"]})
            #authors[abstractId].append({"fullname":row["fullname"],"email":row["email"]})
        
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()
        

    return conference_abstract.util.generate_template('agenda.mako',{"user":user,"request":request,"agendas":agendas,"authors":authors})

