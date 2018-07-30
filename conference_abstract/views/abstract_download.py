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
from conference_abstract.services.data.abstract_info import getAbstract,getAbstractFullDetails,getAbstractHistory
from conference_abstract.services.data.abstract_chair import getAbstractChairs
from conference_abstract.services.data.abstract_topics import getCategories as getAbstractCategories

info_desc = """\
This is the download for abstracts Admins only
"""

service = Service(name='abstractDownload', path='/abstractDownload', description=info_desc)

def valOrBlank(val):
    if val is None:
        return ""
    else:
        return val

def getDownload():
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = """select fk_abstract, cusers.first_name, cusers.middle_initial, cusers.last_name, cusers.email,
title, abstract_type, abstract_text,review_status,
string_agg(replace(authorship.fname || ' ' || authorship.mname || ' ' || authorship.lname, '  ',' '), ', ') as authors,
split_part(replace(replace(replace(selected_topics,'''',''),'{',''),'}',''), ',', 1) AS topic1,
split_part(replace(replace(replace(selected_topics,'''',''),'{',''),'}',''), ',', 2) AS topic2,
split_part(replace(replace(replace(selected_topics,'''',''),'{',''),'}',''), ',', 3) AS topic3,
split_part(replace(replace(replace(selected_topics,'''',''),'{',''),'}',''), ',', 4) AS topic4,
split_part(replace(replace(replace(selected_topics,'''',''),'{',''),'}',''), ',', 5) AS topic5,
split_part(replace(replace(replace(selected_topics,'''',''),'{',''),'}',''), ',', 6) AS topic6,
split_part(replace(replace(replace(selected_topics,'''',''),'{',''),'}',''), ',', 7) AS topic7
--,split_part(replace(replace(replace(selected_topics,'''',''),'{',''),'}',''), ',', 8) AS topic8
,split_part(scorereviewers.reviewer_scores,',',1) as review1
,split_part(scorereviewers.reviewer_scores,',',2) as review2
,split_part(scorereviewers.reviewer_scores,',',3) as review3
,split_part(scorereviewers.reviewer_scores,',',4) as review4
,split_part(scorereviewers.reviewer_scores,',',5) as review5
,split_part(scorereviewers.reviewer_scores,',',6) as review6
,split_part(scorereviewers.reviewer_scores,',',7) as review7
,split_part(scorereviewers.reviewer_scores,',',8) as review8
,split_part(scorereviewers.reviewer_scores,',',9) as review9
,split_part(scorereviewers.reviewer_scores,',',10) as review10
from abstracts 
left join authorship on abstracts.id = authorship.fk_abstract
left join cusers on abstracts.fk_submitter = cusers.id
left join (
select fk_abstracts, string_agg(scores.reviewer_score,',') as reviewer_scores from (
select fk_abstracts, score || ':' || fullname as reviewer_score from abstracts_score 
left join chairs on abstracts_score.fk_reviewer = chairs.id) as scores
group by scores.fk_abstracts, scores.reviewer_score
) as scorereviewers on abstracts.id = scorereviewers.fk_abstracts
where abstracts.review_status != 'UNSUBMITTED'
group by fk_abstract, cusers.first_name, cusers.last_name, cusers.middle_initial, cusers.email, title, abstract_type, abstract_text, selected_topics, scorereviewers.reviewer_scores, review_status
    """
    cur.execute(sql)
    tsv = "Abstract ID\tReview Status\tFirst Name\tMiddle Initial\tLast Name\tSubmitter Email\tTitle\tType\tAbstract Text\tAuthors\tTopic 1\tTopic 2\tTopic 3\tTopic 4\tTopic 5\tTopic 6\tTopic 7\tReview 1\tReview 2\tReview 3\tReview 4\tReview 5\tReview 6\tReview 7\tReview 8\tReview 9\tReview 10\r\n"
    for row in cur:
        tsv+=valOrBlank(str(row["fk_abstract"]))+"\t"
        tsv+=valOrBlank(row["review_status"])+"\t"
        tsv+=valOrBlank(row["first_name"])+"\t"
        tsv+=valOrBlank(row["middle_initial"])+"\t"
        tsv+=valOrBlank(row["last_name"])+"\t"
        tsv+=valOrBlank(row["email"])+"\t"
        tsv+=valOrBlank(row["title"])+"\t"
        tsv+=valOrBlank(row["abstract_type"])
        tsv+='\t"'+valOrBlank(row["abstract_text"].replace("\n\n","@~|~@").replace('"',"'").replace("\n","").replace("@~|~@","\r\n\r\n"))+'"\t'
        tsv+=valOrBlank(row["authors"])+"\t"
        tsv+=valOrBlank(row["topic1"])+"\t"
        tsv+=valOrBlank(row["topic2"])+"\t"
        tsv+=valOrBlank(row["topic3"])+"\t"
        tsv+=valOrBlank(row["topic4"])+"\t"
        tsv+=valOrBlank(row["topic5"])+"\t"
        tsv+=valOrBlank(row["topic6"])+"\t"
        tsv+=valOrBlank(row["topic7"])+"\t"
        tsv+=valOrBlank(row["review1"])+"\t"
        tsv+=valOrBlank(row["review2"])+"\t"
        tsv+=valOrBlank(row["review3"])+"\t"
        tsv+=valOrBlank(row["review4"])+"\t"
        tsv+=valOrBlank(row["review5"])+"\t"
        tsv+=valOrBlank(row["review6"])+"\t"
        tsv+=valOrBlank(row["review7"])+"\t"
        tsv+=valOrBlank(row["review8"])+"\t"
        tsv+=valOrBlank(row["review9"])+"\t"
        tsv+=valOrBlank(row["review10"])+"\r\n"
    tsv.decode('utf-8').encode('utf-8-sig')
    conn.close()

    ##### Convert TSV (utf-8) into XLSX ...
    #
    def tsv_to_xlsx(tsv):
        import StringIO
        tsv_as_fileobj = StringIO.StringIO()
        tsv_as_fileobj.write(tsv)
        tsv_as_fileobj.seek(0)
        xlsx_as_fileobj = StringIO.StringIO()
        import pandas as pd
        writer = pd.ExcelWriter(xlsx_as_fileobj, engine="xlsxwriter")
        tsv_as_df = pd.read_csv(tsv_as_fileobj, sep="\t", encoding="utf-8")
        tsv_as_df.to_excel(writer)
        writer.save()
        xlsx_as_str = xlsx_as_fileobj.getvalue()
        return xlsx_as_str

    tsv = tsv_to_xlsx(tsv)
    #
    #####

    return tsv

@service.get()
def service_get(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
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
        if user.is_admin():
            content = getDownload()
            #can any admin / chair go to the pages?
            if content is not None:
                return conference_abstract.util.generate_xlsx_response(content,'abstracts.xlsx')
                #return conference_abstract.util.generate_tsv_response(content,'abstracts.xls')
            else:
                templateVars["user"] = user
                #no abstract found
                return conference_abstract.util.generate_template('abstractNotFound.mako',templateVars)
        else:
            return conference_abstract.util.generate_template('noAccess.mako',templateVars)
    else:
        #check if it is a reviewer with thier access key.
        pass
    return conference_abstract.util.generate_template('noAccess.mako',templateVars)
