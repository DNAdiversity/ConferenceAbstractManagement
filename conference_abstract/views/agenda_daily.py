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
This is the daily agenda for the conference
"""

service = Service(name='daily agenda', path='/agenda/daily', description=info_desc)

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
        ##sql = """select agenda.*, abstracts.title, abstracts.abstract_text, abstract_type, abstract_text_edited, authorlist.all_authors, fk_authorship from agenda left join abstracts on agenda.fk_abstracts = abstracts.id left join authorlist on authorlist.fk_abstract = abstracts.id left join abstracts_presenting on abstracts_presenting.fk_abstracts = abstracts.id order by agenda.date_time, agenda.room_name, agenda.session_order;"""
        sql = """select dailyagenda.*, speaker,abstract_type from
(select distinct date_time, room_name, session_name, session_id, chair from agenda
where chair is not null
order by date_time, room_name) as dailyagenda
left join
(
select agenda.session_name, array_agg(replace(authorship.fname || ' ' ||  authorship.mname || ' ' ||authorship.lname, '  ', ' ')order by session_order) as speaker from agenda 
left join abstracts_presenting on agenda.fk_abstracts = abstracts_presenting.fk_abstracts
left join authorship on abstracts_presenting.fk_authorship = authorship.id
where fk_authorship is not null
group by session_name
) as speakersbysession
on dailyagenda.session_name = speakersbysession.session_name
left join 
(
select distinct agenda.session_name, abstracts.abstract_type from agenda left join abstracts on agenda.fk_abstracts = abstracts.id where agenda.fk_abstracts is not null
) as sessiontype
on dailyagenda.session_name = sessiontype.session_name
order by date_time, room_name
        """
        print cur.mogrify(sql)
        cur.execute(sql)
        for row in cur.fetchall():
            agendas.append({
                "session_id":row["session_id"],
                "session_name":row["session_name"],
                "room_name":row["room_name"],
                "date_time":row["date_time"],
                "chair":row["chair"],
                "speakers":row["speaker"],
                "type":row["abstract_type"]
            })


    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    conn.close()


    return conference_abstract.util.generate_template('agendaDaily.mako',{"user":user,"request":request,"agendas":agendas,"authors":authors})

